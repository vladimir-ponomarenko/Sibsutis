#include <iostream>
#include <map>
#include <vector>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <fstream>

#define BUFFER_SIZE 1024
#define DATA_SIZE 512

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

struct ClientSession {
    uint32_t total_packets;
    std::vector<Packet> packets;
    std::vector<bool> received;
};

std::map<std::string, ClientSession> sessions;
std::map<int, int> loss_map;

void handle_packet(int sockfd, const struct sockaddr_in &client_addr, const Packet &pkt) {
    char client_key[INET_ADDRSTRLEN + 6];
    inet_ntop(AF_INET, &client_addr.sin_addr, client_key, INET_ADDRSTRLEN);
    sprintf(client_key + strlen(client_key), ":%d", ntohs(client_addr.sin_port));

    // Проверяем, нужно ли имитировать потерю пакета
    auto it = loss_map.find(pkt.seq_num);
    if (it != loss_map.end() && it->second > 0) {
        it->second--; // Уменьшаем счетчик потерь
        std::cout << "Simulated loss of packet " << pkt.seq_num << " for " << client_key << std::endl;
        return; // Не обрабатываем пакет, имитируем потерю
    }

    if (pkt.seq_num >= pkt.total_packets) {
        std::cerr << "Invalid seq_num " << pkt.seq_num << " from " << client_key << std::endl;
        return;
    }

    auto &session = sessions[client_key];
    if (session.total_packets == 0) {
        session.total_packets = pkt.total_packets;
        session.packets.resize(pkt.total_packets);
        session.received.resize(pkt.total_packets, false);
    }

    if (!session.received[pkt.seq_num]) {
        session.packets[pkt.seq_num] = pkt;
        session.received[pkt.seq_num] = true;
        std::cout << "Received packet " << pkt.seq_num << "/" << pkt.total_packets << " from " << client_key << std::endl;
    }

    Ack ack{pkt.seq_num};
    sendto(sockfd, &ack, sizeof(ack), 0, (struct sockaddr*)&client_addr, sizeof(client_addr));

    bool all_received = true;
    for (bool r : session.received) {
        if (!r) {
            all_received = false;
            break;
        }
    }

    if (all_received) {
        std::string filename = "received_";
        filename += client_key;
        filename += ".dat";
        std::ofstream outfile(filename, std::ios::binary);
        for (const auto &p : session.packets) {
            outfile.write(p.data, p.data_length);
        }
        outfile.close();
        std::cout << "File saved as " << filename << std::endl;
        sessions.erase(client_key);
    }
}

int main(int argc, char *argv[]) {
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(0);

    if (bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    socklen_t len = sizeof(server_addr);
    getsockname(sockfd, (struct sockaddr*)&server_addr, &len);
    std::cout << "Server port: " << ntohs(server_addr.sin_port) << std::endl;

    // Обработка аргументов для имитации потерь
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-p") == 0) {
            if (i + 2 >= argc) {
                std::cerr << "Invalid arguments for -p" << std::endl;
                continue;
            }
            int seq = atoi(argv[++i]);
            int cnt = atoi(argv[++i]);
            if (seq < 0 || cnt <= 0) {
                std::cerr << "Invalid values for -p: seq=" << seq << ", cnt=" << cnt << std::endl;
                continue;
            }
            loss_map[seq] = cnt;
            std::cout << "Simulating loss of packet " << seq << " (" << cnt << " times)" << std::endl;
        }
    }

    while (true) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        char buffer[BUFFER_SIZE];
        int recv_len = recvfrom(sockfd, buffer, BUFFER_SIZE, 0, (struct sockaddr*)&client_addr, &client_len);
        if (recv_len <= 0) {
            continue;
        }

        if (recv_len < (ssize_t)(sizeof(Packet) - DATA_SIZE)) {
            std::cerr << "Invalid packet size" << std::endl;
            continue;
        }

        Packet *pkt = (Packet*)buffer;
        handle_packet(sockfd, client_addr, *pkt);
    }

    close(sockfd);
    return 0;
}