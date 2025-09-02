#include "common.h"


void generate_uuid(char *output) {
    uuid_t uuid;
    uuid_generate(uuid);
    uuid_unparse_lower(uuid, output);
}

void get_timestamp(char *buffer) {
    time_t now = time(NULL);
    struct tm tm_info;

    strftime(buffer, TIMESTAMP_SIZE, "%Y-%m-%d %H:%M:%S",
             localtime_r(&now, &tm_info));
}

void sleep_ms(long ms) {
    if (ms <= 0) return;
    struct timespec ts;
    ts.tv_sec = ms / 1000;
    ts.tv_nsec = (ms % 1000) * 1000000L;

    while (nanosleep(&ts, &ts) == -1 && errno == EINTR);
}

static int send_multipart(void *socket, int flags, const void *data1,
                          size_t size1, const void *data2, size_t size2) {
    if (zmq_send(socket, data1, size1, flags | ZMQ_SNDMORE) == -1) return -1;
    if (zmq_send(socket, data2, size2, flags) == -1) return -1;
    return 0;
}

int dealer_send(void *dealer, const chat_message_t *msg) {
    return send_multipart(dealer, 0, "", 0, msg, sizeof(chat_message_t));
}

int router_send(void *router, const char *client_id,
                const chat_message_t *msg) {
    if (zmq_send(router, client_id, strlen(client_id), ZMQ_SNDMORE) == -1)
        return -1;
    return dealer_send(router, msg);
}

int dealer_recv(void *dealer, chat_message_t *msg_out) {
    int rc = -1;
    zmq_msg_t empty_frame, payload_frame;

    if (zmq_msg_init(&empty_frame) != 0) goto cleanup;
    if (zmq_msg_init(&payload_frame) != 0) goto cleanup_empty;

    if (zmq_msg_recv(&empty_frame, dealer, 0) == -1) goto cleanup_both;
    if (!zmq_msg_more(&empty_frame)) goto cleanup_both;

    if (zmq_msg_recv(&payload_frame, dealer, 0) == -1) goto cleanup_both;
    if (zmq_msg_size(&payload_frame) != sizeof(chat_message_t))
        goto cleanup_both;

    memcpy(msg_out, zmq_msg_data(&payload_frame), sizeof(chat_message_t));
    rc = 0;

cleanup_both:
    zmq_msg_close(&payload_frame);
cleanup_empty:
    zmq_msg_close(&empty_frame);
cleanup:
    return rc;
}

int router_recv(void *router, char *client_id_out, size_t id_out_size,
                chat_message_t *msg_out) {
    int rc = -1;
    zmq_msg_t id_frame;

    if (zmq_msg_init(&id_frame) != 0) return -1;

    if (zmq_msg_recv(&id_frame, router, 0) == -1) {
        zmq_msg_close(&id_frame);
        return -1;
    }

    size_t id_len = zmq_msg_size(&id_frame);

    snprintf(client_id_out, id_out_size, "%.*s", (int)id_len,
             (char *)zmq_msg_data(&id_frame));
    zmq_msg_close(&id_frame);

    if (dealer_recv(router, msg_out) != 0) {
        return -1;
    }

    rc = 0;
    return rc;
}