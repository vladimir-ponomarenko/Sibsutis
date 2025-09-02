#include <assert.h>
#include <signal.h>
#include "common.h"


typedef struct {
    char client_id[CLIENT_ID_SIZE];
    time_t last_heartbeat;
    int active;
} client_info_t;

static client_info_t clients[MAX_CLIENTS];
static pthread_mutex_t clients_mutex = PTHREAD_MUTEX_INITIALIZER;
static volatile sig_atomic_t server_running = 1;

/**
 * @brief Обработчик сигналов для корректного завершения работы сервера.
 */
static void signal_handler(int signum) {
    (void)signum;
    server_running = 0;
}

/**
 * @brief Добавляет нового клиента в список.
 * @param client_id Идентификатор клиента.
 * @return Индекс клиента в массиве или -1, если нет места.
 */
static int add_client(const char *client_id) {
    pthread_mutex_lock(&clients_mutex);
    int index = -1;
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (!clients[i].active) {
            index = i;
            break;
        }
    }

    if (index != -1) {
        snprintf(clients[index].client_id, sizeof(clients[index].client_id),
                 "%s", client_id);
        clients[index].last_heartbeat = time(NULL);
        clients[index].active = 1;
    }
    pthread_mutex_unlock(&clients_mutex);
    return index;
}

/**
 * @brief Деактивирует клиента по его идентификатору.
 * @param client_id Идентификатор клиента.
 */
static void remove_client(const char *client_id) {
    pthread_mutex_lock(&clients_mutex);
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (clients[i].active && strcmp(clients[i].client_id, client_id) == 0) {
            clients[i].active = 0;
            break;
        }
    }
    pthread_mutex_unlock(&clients_mutex);
}

/**
 * @brief Широковещательная рассылка сообщения всем активным клиентам.
 * @param router_socket ROUTER-сокет.
 * @param msg Сообщение для отправки.
 * @param exclude_client_id ID клиента для исключения из рассылки (может быть
 * NULL).
 */
static void broadcast_message(void *router_socket, const chat_message_t *msg,
                              const char *exclude_client_id) {
    pthread_mutex_lock(&clients_mutex);
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (!clients[i].active) continue;
        if (exclude_client_id &&
            strcmp(clients[i].client_id, exclude_client_id) == 0)
            continue;

        if (router_send(router_socket, clients[i].client_id, msg) != 0) {
            if (zmq_errno() != ETERM) {
                fprintf(stderr, "Ошибка отправки сообщения клиенту %s: %s\n",
                        clients[i].client_id, zmq_strerror(zmq_errno()));
            }
        }
    }
    pthread_mutex_unlock(&clients_mutex);
}

/**
 * @brief Поток, проверяющий активность клиентов по heartbeat-сообщениям.
 */
static void *heartbeat_checker(void *arg) {
    (void)arg;
    while (server_running) {
        sleep_ms(HEARTBEAT_INTERVAL_MS);

        pthread_mutex_lock(&clients_mutex);
        time_t now = time(NULL);
        for (int i = 0; i < MAX_CLIENTS; i++) {
            if (clients[i].active) {
                double diff = difftime(now, clients[i].last_heartbeat);
                if (diff >
                    (double)(HEARTBEAT_INTERVAL_MS * HEARTBEAT_TIMEOUT_FACTOR) /
                        1000.0) {
                    printf("Клиент %s отключен по таймауту.\n",
                           clients[i].client_id);
                    clients[i].active = 0;
                }
            }
        }
        pthread_mutex_unlock(&clients_mutex);
    }
    return NULL;
}

/**
 * @brief Обрабатывает входящее сообщение от клиента.
 */
static void process_message(void *router, const char *client_id,
                            const chat_message_t *msg) {
    pthread_mutex_lock(&clients_mutex);
    int client_idx = -1;
    for (int i = 0; i < MAX_CLIENTS; ++i) {
        if (clients[i].active && strcmp(clients[i].client_id, client_id) == 0) {
            client_idx = i;
            break;
        }
    }
    pthread_mutex_unlock(&clients_mutex);

    switch (msg->type) {
        case MSG_TYPE_JOIN:
            if (client_idx == -1) {
                if (add_client(client_id) != -1) {
                    printf("Клиент %s присоединился.\n", client_id);
                    chat_message_t welcome_msg = {0};
                    snprintf(welcome_msg.client_id,
                             sizeof(welcome_msg.client_id), "Server");
                    welcome_msg.type = MSG_TYPE_WELCOME;
                    get_timestamp(welcome_msg.timestamp);
                    snprintf(welcome_msg.content, sizeof(welcome_msg.content),
                             "Добро пожаловать в чат!");
                    router_send(router, client_id, &welcome_msg);
                } else {
                    fprintf(
                        stderr,
                        "Сервер переполнен. Не удалось добавить клиента %s\n",
                        client_id);
                }
            }
            break;
        case MSG_TYPE_HEARTBEAT:
            if (client_idx != -1) {
                pthread_mutex_lock(&clients_mutex);
                clients[client_idx].last_heartbeat = time(NULL);
                pthread_mutex_unlock(&clients_mutex);
            }
            break;
        case MSG_TYPE_TEXT:
            if (client_idx != -1) {
                printf("Сообщение от %s: %s\n", client_id, msg->content);
                broadcast_message(router, msg, client_id);
            }
            break;
        case MSG_TYPE_LEAVE:
            if (client_idx != -1) {
                printf("Клиент %s покинул чат.\n", client_id);
                remove_client(client_id);
            }
            break;
        default:
            fprintf(stderr, "Неизвестный тип сообщения %d от клиента %s\n",
                    msg->type, client_id);
            break;
    }
}

int main(void) {
    struct sigaction sa = {.sa_handler = signal_handler};
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    void *context = zmq_ctx_new();
    assert(context);
    void *router = zmq_socket(context, ZMQ_ROUTER);
    assert(router);

    int rcv_timeout = ROUTER_RCV_TIMEOUT_MS;
    zmq_setsockopt(router, ZMQ_RCVTIMEO, &rcv_timeout, sizeof(rcv_timeout));

    if (zmq_bind(router, SERVER_ENDPOINT) != 0) {
        perror("zmq_bind");
        zmq_close(router);
        zmq_ctx_destroy(context);
        return EXIT_FAILURE;
    }
    printf("Сервер запущен на %s\n", SERVER_ENDPOINT);

    pthread_t hb_thread;
    pthread_create(&hb_thread, NULL, heartbeat_checker, NULL);

    while (server_running) {
        char client_id[CLIENT_ID_SIZE];
        chat_message_t msg;

        if (router_recv(router, client_id, sizeof(client_id), &msg) == 0) {
            process_message(router, client_id, &msg);
        } else {
            if (zmq_errno() != EAGAIN && server_running) {
                fprintf(stderr, "Ошибка router_recv: %s\n",
                        zmq_strerror(zmq_errno()));
            }
        }
    }

    printf("\nЗавершение работы сервера...\n");
    pthread_join(hb_thread, NULL);
    zmq_close(router);
    zmq_ctx_destroy(context);
    printf("Сервер остановлен.\n");
    return EXIT_SUCCESS;
}