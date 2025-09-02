#ifndef CHAT_COMMON_H
#define CHAT_COMMON_H

#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <uuid/uuid.h>
#include <zmq.h>

#define SERVER_ENDPOINT "tcp://*:5555"
#define CLIENT_ENDPOINT "tcp://127.0.0.1:5555"
#define MAX_MESSAGE_LENGTH 256
#define MAX_CLIENTS 100
#define HEARTBEAT_INTERVAL_MS 2500
#define HEARTBEAT_TIMEOUT_FACTOR 3
#define ROUTER_RCV_TIMEOUT_MS 500
#define DEALER_RCV_TIMEOUT_MS 100
#define DEALER_SND_TIMEOUT_MS 1000
#define CLIENT_ID_SIZE 37
#define TIMESTAMP_SIZE 20


/**
 * @brief Перечисление типов сообщений в чате.
 */
typedef enum {
    MSG_TYPE_TEXT = 1,
    MSG_TYPE_JOIN = 2,
    MSG_TYPE_LEAVE = 3,
    MSG_TYPE_HEARTBEAT = 4,
    MSG_TYPE_SYSTEM = 5,
    MSG_TYPE_WELCOME = 6,
    MSG_TYPE_ERROR = 7
} message_type_t;

/**
 * @brief Структура, представляющая одно сообщение в чате.
 *
 * Все строковые поля гарантированно завершаются нулевым символом.
 */
typedef struct {
    char client_id[CLIENT_ID_SIZE];
    message_type_t type;
    char timestamp[TIMESTAMP_SIZE];
    char content[MAX_MESSAGE_LENGTH];
} chat_message_t;

/**
 * @brief Генерирует уникальный идентификатор (UUID).
 * @param output Буфер для записи UUID (размером не менее CLIENT_ID_SIZE).
 */
void generate_uuid(char *output);

/**
 * @brief Получает текущую метку времени в формате "YYYY-MM-DD HH:MM:SS".
 * @param buffer Буфер для записи времени (размером не менее TIMESTAMP_SIZE).
 */
void get_timestamp(char *buffer);

/**
 * @brief Безопасно приостанавливает выполнение потока на заданное число
 * миллисекунд.
 *
 * Функция корректно обрабатывает прерывания сигналами (EINTR).
 * @param ms Количество миллисекунд для сна.
 */
void sleep_ms(long ms);

/**
 * @brief Отправляет сообщение через сокет DEALER.
 *
 * Формирует multipart-сообщение: [empty_frame][payload].
 * @param dealer DEALER-сокет.
 * @param msg Указатель на сообщение для отправки.
 * @return 0 в случае успеха, -1 в случае ошибки.
 */
int dealer_send(void *dealer, const chat_message_t *msg);

/**
 * @brief Получает сообщение на сокете DEALER.
 *
 * Ожидает multipart-сообщение: [empty_frame][payload].
 * @param dealer DEALER-сокет.
 * @param msg_out Указатель на структуру для сохранения полученного сообщения.
 * @return 0 в случае успеха, -1 в случае ошибки (включая таймаут).
 */
int dealer_recv(void *dealer, chat_message_t *msg_out);

/**
 * @brief Отправляет сообщение через сокет ROUTER конкретному клиенту.
 *
 * Формирует multipart-сообщение: [client_identity][empty_frame][payload].
 * @param router ROUTER-сокет.
 * @param client_id Идентификатор клиента-получателя.
 * @param msg Указатель на сообщение для отправки.
 * @return 0 в случае успеха, -1 в случае ошибки.
 */
int router_send(void *router, const char *client_id, const chat_message_t *msg);

/**
 * @brief Получает сообщение на сокете ROUTER.
 *
 * Ожидает multipart-сообщение: [client_identity][empty_frame][payload].
 * @param router ROUTER-сокет.
 * @param client_id_out Буфер для сохранения идентификатора клиента.
 * @param id_out_size Размер буфера client_id_out.
 * @param msg_out Указатель на структуру для сохранения полученного сообщения.
 * @return 0 в случае успеха, -1 в случае ошибки (включая таймаут).
 */
int router_recv(void *router, char *client_id_out, size_t id_out_size,
                chat_message_t *msg_out);

#endif