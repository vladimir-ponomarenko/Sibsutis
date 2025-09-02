#include <assert.h>
#include "common.h"


/**
 * @brief Глобальное состояние клиента, передаваемое в потоки
 */
typedef struct {
    void *context;
    void *dealer;
    char client_id[CLIENT_ID_SIZE];
    volatile sig_atomic_t running;
} client_state_t;

/**
 * @brief Поток, периодически отправляющий heartbeat-сообщения на сервер.
 */
static void *heartbeat_sender(void *arg) {
    client_state_t *state = (client_state_t *)arg;
    while (state->running) {
        sleep_ms(HEARTBEAT_INTERVAL_MS);
        chat_message_t hb = {0};
        snprintf(hb.client_id, sizeof(hb.client_id), "%s", state->client_id);
        hb.type = MSG_TYPE_HEARTBEAT;
        get_timestamp(hb.timestamp);

        if (dealer_send(state->dealer, &hb) != 0 && state->running) {
            fprintf(stderr, "Ошибка отправки heartbeat: %s\n",
                    zmq_strerror(zmq_errno()));
        }
    }
    return NULL;
}

/**
 * @brief Поток, принимающий и отображающий сообщения от сервера.
 */
static void *message_receiver(void *arg) {
    client_state_t *state = (client_state_t *)arg;
    while (state->running) {
        chat_message_t msg;
        if (dealer_recv(state->dealer, &msg) == 0) {
            printf("[%s] %s: %s\n", msg.timestamp, msg.client_id, msg.content);
        } else if (state->running && zmq_errno() != EAGAIN) {
            fprintf(stderr, "Ошибка получения сообщения: %s\n",
                    zmq_strerror(zmq_errno()));
            state->running = 0;
        }
    }
    return NULL;
}

/**
 * @brief Отправляет текстовое сообщение от пользователя на сервер.
 */
static void send_user_message(client_state_t *state, const char *input) {
    chat_message_t msg = {0};
    msg.type = MSG_TYPE_TEXT;
    get_timestamp(msg.timestamp);
    snprintf(msg.client_id, sizeof(msg.client_id), "%s", state->client_id);
    snprintf(msg.content, sizeof(msg.content), "%s", input);

    if (dealer_send(state->dealer, &msg) != 0) {
        fprintf(stderr, "Ошибка отправки сообщения: %s\n",
                zmq_strerror(zmq_errno()));
    }
}

/**
 * @brief Инициализирует сокет DEALER и его параметры.
 */
static void *setup_dealer_socket(client_state_t *state) {
    void *dealer = zmq_socket(state->context, ZMQ_DEALER);
    assert(dealer);

    zmq_setsockopt(dealer, ZMQ_IDENTITY, state->client_id,
                   strlen(state->client_id));
    int rcv_timeout = DEALER_RCV_TIMEOUT_MS;
    int snd_timeout = DEALER_SND_TIMEOUT_MS;
    zmq_setsockopt(dealer, ZMQ_RCVTIMEO, &rcv_timeout, sizeof(rcv_timeout));
    zmq_setsockopt(dealer, ZMQ_SNDTIMEO, &snd_timeout, sizeof(snd_timeout));

    if (zmq_connect(dealer, CLIENT_ENDPOINT) != 0) {
        perror("zmq_connect");
        zmq_close(dealer);
        return NULL;
    }
    return dealer;
}

int main(void) {
    client_state_t state = {.running = 1};
    generate_uuid(state.client_id);

    state.context = zmq_ctx_new();
    assert(state.context);

    state.dealer = setup_dealer_socket(&state);
    if (!state.dealer) {
        zmq_ctx_destroy(state.context);
        return EXIT_FAILURE;
    }
    printf("Клиент запущен. ID: %s. Введите 'quit' для выхода.\n",
           state.client_id);

    chat_message_t join_msg = {0};
    join_msg.type = MSG_TYPE_JOIN;
    get_timestamp(join_msg.timestamp);
    snprintf(join_msg.client_id, sizeof(join_msg.client_id), "%s",
             state.client_id);
    snprintf(join_msg.content, sizeof(join_msg.content),
             "Присоединяюсь к чату");

    if (dealer_send(state.dealer, &join_msg) != 0) {
        fprintf(stderr, "Не удалось отправить JOIN: %s\n",
                zmq_strerror(zmq_errno()));
        zmq_close(state.dealer);
        zmq_ctx_destroy(state.context);
        return EXIT_FAILURE;
    }

    pthread_t hb_thread, rx_thread;
    pthread_create(&hb_thread, NULL, heartbeat_sender, &state);
    pthread_create(&rx_thread, NULL, message_receiver, &state);

    char input_buffer[MAX_MESSAGE_LENGTH];
    while (state.running && fgets(input_buffer, sizeof(input_buffer), stdin)) {
        input_buffer[strcspn(input_buffer, "\n")] = '\0';
        if (strcmp(input_buffer, "quit") == 0) break;
        if (strlen(input_buffer) > 0) {
            send_user_message(&state, input_buffer);
        }
    }

    state.running = 0;

    chat_message_t leave_msg = {0};
    leave_msg.type = MSG_TYPE_LEAVE;
    get_timestamp(leave_msg.timestamp);
    snprintf(leave_msg.client_id, sizeof(leave_msg.client_id), "%s",
             state.client_id);
    dealer_send(state.dealer, &leave_msg);

    pthread_join(rx_thread, NULL);
    pthread_join(hb_thread, NULL);

    zmq_close(state.dealer);
    zmq_ctx_destroy(state.context);
    printf("Клиент остановлен.\n");

    return EXIT_SUCCESS;
}