#include <iostream>
#include <fstream>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <vector>

#define BUFFER_SIZE 1024
#define DATA_SIZE 512
#define MAX_RETRIES 5

#pragma pack(push, 1)
struct Packet {
    uint32_t seq_num;
    uint32_t total_packets;
    uint32_t data_length;
    char data[DATA_SIZE];
};
#pragma pack(pop)

#pragma pack(push, 1)
struct Ack {
    uint32_t seq_num;
};
#pragma pack(pop)

int main(int argc, char *argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0] << " <server_ip> <server_port> <file/message>" << std::endl;
        return 1;
    }

    std::string server_ip = argv[1];
    int server_port = atoi(argv[2]);
    std::string input = argv[3];

    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return 1;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(server_port);
    inet_pton(AF_INET, server_ip.c_str(), &server_addr.sin_addr);

    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 0;
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    std::vector<char> data;
    std::ifstream infile(input);
    if (infile) {
        // Если это файл, читаем его содержимое
        data = std::vector<char>(std::istreambuf_iterator<char>(infile), std::istreambuf_iterator<char>());
    } else {
        // Иначе отправляем сообщение как текст
        data.assign(input.begin(), input.end());
    }

    if (data.empty()) {
        std::cerr << "Empty file or message. Nothing to send." << std::endl;
        close(sockfd);
        return 1;
    }

    uint32_t total_packets = (data.size() + DATA_SIZE - 1) / DATA_SIZE;
    for (uint32_t i = 0; i < total_packets; i++) {
        Packet pkt;
        pkt.seq_num = i;
        pkt.total_packets = total_packets;
        pkt.data_length = std::min(static_cast<size_t>(DATA_SIZE), data.size() - i * DATA_SIZE);
        memcpy(pkt.data, data.data() + i * DATA_SIZE, pkt.data_length);

        int retries = 0;
        while (retries < MAX_RETRIES) {
            ssize_t packet_size = sizeof(Packet) - DATA_SIZE + pkt.data_length;
            if (sendto(sockfd, &pkt, packet_size, 0, (struct sockaddr*)&server_addr, sizeof(server_addr)) != packet_size) {
                perror("sendto");
                continue;
            }

            Ack ack;
            socklen_t len = sizeof(server_addr);
            int recv_len = recvfrom(sockfd, &ack, sizeof(ack), 0, (struct sockaddr*)&server_addr, &len);
            if (recv_len == sizeof(ack) && ack.seq_num == pkt.seq_num) {
                std::cout << "Packet " << i << " acknowledged" << std::endl;
                break;
            }
            retries++;
            std::cout << "Retrying packet " << i << " (" << retries << "/" << MAX_RETRIES << ")" << std::endl;
        }

        if (retries == MAX_RETRIES) {
            std::cerr << "Failed to send packet " << i << std::endl;
            close(sockfd);
            return 1;
        }
    }

    close(sockfd);
    return 0;
}