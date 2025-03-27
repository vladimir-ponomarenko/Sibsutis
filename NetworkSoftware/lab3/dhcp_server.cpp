#include <iostream>
#include <vector>
#include <map>
#include <cstring>
#include <cstdlib>
#include <ctime>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <ifaddrs.h>
#include <net/if.h>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <csignal>
#include <atomic>
#include <thread>
#include <iomanip>

#define DHCP_SERVER_PORT 67
#define DHCP_CLIENT_PORT 68
#define BOOTREQUEST 1
#define BOOTREPLY 2
#define DHCPDISCOVER 1
#define DHCPOFFER 2
#define DHCPREQUEST 3
#define DHCPACK 5
#define DHCPNAK 6
#define DHCPDECLINE 4
#define DHCPRELEASE 7
#define DHCPINFORM 8

struct DHCPMessage {
    uint8_t op;
    uint8_t htype;
    uint8_t hlen;
    uint8_t hops;
    uint32_t xid;
    uint16_t secs;
    uint16_t flags;
    in_addr ciaddr;
    in_addr yiaddr;
    in_addr siaddr;
    in_addr giaddr;
    uint8_t chaddr[16];
    char sname[64];
    char file[128];
    uint8_t options[312];
};

struct Lease {
    in_addr ip_address;
    time_t expiry_time;
    bool declined;
};

std::atomic<bool> keepRunning(true);

void signalHandler(int signum) {
    std::cout << "Interrupt signal (" << signum << ") received.\n";
    keepRunning = false;
}

class DHCPServer {
public:
    DHCPServer(const std::string& ip_range_start, const std::string& ip_range_end,
               const std::string& subnet_mask, const std::string& router, const std::string& dns, int lease_time) :
        ip_range_start_(ip_range_start), ip_range_end_(ip_range_end), subnet_mask_(subnet_mask),
        router_(router), dns_(dns), lease_time_(lease_time), sockfd_(-1) {
        if (!parse_ip_range()) {
            throw std::runtime_error("Invalid IP range.");
        }
        load_leases();
    }

    ~DHCPServer() {
        save_leases();
        if (sockfd_ != -1) {
            close(sockfd_);
        }
    }

    void run() {
        if (!create_socket()) {
            return;
        }

        std::cout << "DHCP Server started. Listening on port " << DHCP_SERVER_PORT << std::endl;

        while (keepRunning) {
            receive_message();
        }
        std::cout << "DHCP Server shutting down." << std::endl;
    }

    void stop() {
        keepRunning = false;
    }

private:
    int sockfd_;
    struct sockaddr_in server_addr_, client_addr_;
    std::string ip_range_start_;
    std::string ip_range_end_;
    in_addr_t ip_start_;
    in_addr_t ip_end_;
    std::string subnet_mask_;
    std::string router_;
    std::string dns_;
    int lease_time_;
    std::map<std::string, Lease> leases_;

    bool parse_ip_range() {
        ip_start_ = ntohl(inet_addr(ip_range_start_.c_str()));
        ip_end_ = ntohl(inet_addr(ip_range_end_.c_str()));
        return (ip_start_ != INADDR_NONE && ip_end_ != INADDR_NONE && ip_start_ <= ip_end_);
    }

    bool create_socket() {
        sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
        if (sockfd_ < 0) {
            perror("socket creation failed");
            return false;
        }

        memset(&server_addr_, 0, sizeof(server_addr_));
        memset(&client_addr_, 0, sizeof(client_addr_));

        server_addr_.sin_family = AF_INET;
        server_addr_.sin_addr.s_addr = INADDR_ANY;
        server_addr_.sin_port = htons(DHCP_SERVER_PORT);

        int broadcast_enable = 1;
        if (setsockopt(sockfd_, SOL_SOCKET, SO_BROADCAST, &broadcast_enable, sizeof(broadcast_enable)) < 0) {
            perror("setsockopt (SO_BROADCAST) failed");
            close(sockfd_);
            return false;
        }

        struct timeval tv;
        tv.tv_sec = 1;
        tv.tv_usec = 0;
        if (setsockopt(sockfd_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
            perror("setsockopt (SO_RCVTIMEO) failed");
            close(sockfd_);
            return false;
        }

        if (bind(sockfd_, (const struct sockaddr *)&server_addr_, sizeof(server_addr_)) < 0) {
            perror("bind failed");
            close(sockfd_);
            return false;
        }
        return true;
    }

    void receive_message() {
        DHCPMessage request, response;
        socklen_t client_addr_len = sizeof(client_addr_);
        memset(&request, 0, sizeof(request));
        memset(&response, 0, sizeof(response));
    
        ssize_t recv_len = recvfrom(sockfd_, &request, sizeof(request), 0,
                                    (struct sockaddr *)&client_addr_, &client_addr_len);
    
        if (recv_len < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                return;
            }
            perror("recvfrom failed");
            return;
        }
    
        std::string client_mac = mac_to_string(request.chaddr, request.hlen);
        std::cout << "Received message from: " << client_mac << " (" << recv_len << " bytes)" << std::endl;
    
        if (request.op == BOOTREQUEST) {
            uint8_t message_type = get_dhcp_message_type(request, recv_len);
            std::cout << "Received DHCP message type: " << (int)message_type << std::endl;
            switch (message_type) {
                case DHCPDISCOVER:
                    handle_dhcp_discover(request, response);
                    break;
                case DHCPREQUEST:
                    handle_dhcp_request(request, response);
                    break;
                case DHCPDECLINE:
                    handle_dhcp_decline(request);
                    break;
                case DHCPRELEASE:
                    handle_dhcp_release(request);
                    break;
                case DHCPINFORM:
                    handle_dhcp_inform(request, response);
                    break;
                default:
                    std::cout << "Unknown DHCP message type: " << (int)message_type << std::endl;
            }
        }
    }

    void handle_dhcp_discover(const DHCPMessage& request, DHCPMessage& response) {
        prepare_dhcp_response(request, response, DHCPOFFER);
        in_addr_t offered_ip = find_available_ip(request);
        if (offered_ip == INADDR_NONE) {
            std::cerr << "No available IP addresses." << std::endl;
            return;
        }
        response.yiaddr.s_addr = htonl(offered_ip);
        add_dhcp_options(response, offered_ip);
        send_dhcp_response(request, response);
    }

    void handle_dhcp_request(const DHCPMessage& request, DHCPMessage& response) {
        prepare_dhcp_response(request, response, DHCPACK);
        in_addr requested_ip;
        bool requested_ip_found = get_requested_ip(request, requested_ip);

        if (!requested_ip_found) {
            if (request.ciaddr.s_addr != 0) {
                response.yiaddr = request.ciaddr;
                prepare_dhcp_response(request, response, DHCPNAK);
                send_dhcp_response(request, response, true);
            } else {
                prepare_dhcp_response(request, response, DHCPNAK);
                send_dhcp_response(request, response);
            }
            std::cerr << "DHCPREQUEST does not contain a requested IP." << std::endl;
            return;
        }

        std::string client_mac = mac_to_string(request.chaddr, request.hlen);
        auto lease_it = leases_.find(client_mac);

        if (lease_it != leases_.end()) {
            if (lease_it->second.ip_address.s_addr == requested_ip.s_addr &&
                lease_it->second.expiry_time > time(nullptr) && !lease_it->second.declined) {
                response.yiaddr = requested_ip;
                lease_it->second.expiry_time = time(nullptr) + lease_time_;
                std::cout << "Renewed lease for " << inet_ntoa(requested_ip) << " to " << client_mac << std::endl;
            } else if (lease_it->second.declined) {
                if (is_ip_available(ntohl(requested_ip.s_addr))) {
                    response.yiaddr = requested_ip;
                    leases_[client_mac] = {requested_ip, time(nullptr) + lease_time_, false};
                    std::cout << "Assigned declined IP " << inet_ntoa(requested_ip) << " to " << client_mac << std::endl;
                } else {
                    prepare_dhcp_response(request, response, DHCPNAK);
                    send_dhcp_response(request, response);
                    std::cerr << "Requested IP is not available." << std::endl;
                    return;
                }
            } else {
                if (is_ip_available(ntohl(requested_ip.s_addr)) || (lease_it->second.expiry_time <= time(nullptr))) {
                    response.yiaddr = requested_ip;
                    leases_[client_mac] = {requested_ip, time(nullptr) + lease_time_, false};
                    std::cout << "Assigned new IP " << inet_ntoa(requested_ip) << " to " << client_mac << std::endl;
                } else {
                    prepare_dhcp_response(request, response, DHCPNAK);
                    send_dhcp_response(request, response);
                    std::cerr << "Requested IP is not available." << std::endl;
                    return;
                }
            }
        } else {
            if (is_ip_available(ntohl(requested_ip.s_addr))) {
                response.yiaddr = requested_ip;
                leases_[client_mac] = {requested_ip, time(nullptr) + lease_time_, false};
                std::cout << "Assigned IP " << inet_ntoa(requested_ip) << " to " << client_mac << std::endl;
            } else {
                prepare_dhcp_response(request, response, DHCPNAK);
                send_dhcp_response(request, response);
                std::cerr << "Requested IP is not available." << std::endl;
                return;
            }
        }

        add_dhcp_options(response, ntohl(requested_ip.s_addr));
        send_dhcp_response(request, response);
    }

    void handle_dhcp_decline(const DHCPMessage& request) {
        std::string client_mac = mac_to_string(request.chaddr, request.hlen);
        auto it = leases_.find(client_mac);
        if (it != leases_.end()) {
            it->second.declined = true;
            std::cout << "Marked IP " << inet_ntoa(it->second.ip_address) << " as declined by " << client_mac << std::endl;
        }
    }

    void handle_dhcp_release(const DHCPMessage& request) {
        std::string client_mac = mac_to_string(request.chaddr, request.hlen);
        auto it = leases_.find(client_mac);
        if (it != leases_.end()) {
            leases_.erase(it);
            std::cout << "Released IP " << inet_ntoa(it->second.ip_address) << " from " << client_mac << std::endl;
        }
    }

    void handle_dhcp_inform(const DHCPMessage& request, DHCPMessage& response) {
        prepare_dhcp_response(request, response, DHCPACK);
        response.yiaddr = request.ciaddr;
        in_addr_t client_ip = ntohl(request.ciaddr.s_addr);
        add_dhcp_options(response, client_ip, true);
        send_dhcp_response(request, response, true);
    }

    void prepare_dhcp_response(const DHCPMessage& request, DHCPMessage& response, uint8_t message_type) {
        response.op = BOOTREPLY;
        response.htype = request.htype;
        response.hlen = request.hlen;
        response.hops = 0;
        response.xid = request.xid;
        response.secs = 0;
        response.flags = request.flags;
        response.ciaddr.s_addr = 0;
        response.siaddr = get_server_ip();
        response.giaddr = request.giaddr;
        memcpy(response.chaddr, request.chaddr, sizeof(response.chaddr));
        memset(response.sname, 0, sizeof(response.sname));
        memset(response.file, 0, sizeof(response.file));

        // Magic cookie
        response.options[0] = 99;
        response.options[1] = 130;
        response.options[2] = 83;
        response.options[3] = 99;

        int options_offset = 4; // Start after magic cookie
        add_option(response, 53, &message_type, 1, options_offset);
    }

    in_addr_t find_available_ip(const DHCPMessage& request) {
        std::string client_mac = mac_to_string(request.chaddr, request.hlen);
        auto lease_it = leases_.find(client_mac);
        if (lease_it != leases_.end() && lease_it->second.expiry_time > time(nullptr) && !lease_it->second.declined) {
            return ntohl(lease_it->second.ip_address.s_addr);
        }

        in_addr requested_ip;
        if (get_requested_ip(request, requested_ip)) {
            in_addr_t requested_ip_n = ntohl(requested_ip.s_addr);
            if (is_ip_available(requested_ip_n)) {
                return requested_ip_n;
            }
        }

        for (in_addr_t ip = ip_start_; ip <= ip_end_; ++ip) {
            if (is_ip_available(ip)) {
                return ip;
            }
        }

        return INADDR_NONE;
    }

    bool is_ip_available(in_addr_t ip) {
        if (ip < ip_start_ || ip > ip_end_) {
            return false;
        }
        for (const auto& lease_pair : leases_) {
            if (lease_pair.second.expiry_time > time(nullptr) &&
                ntohl(lease_pair.second.ip_address.s_addr) == ip && !lease_pair.second.declined) {
                return false;
            }
        }
        return true;
    }

    bool get_requested_ip(const DHCPMessage& message, in_addr& requested_ip) {
        const uint8_t* raw_data = reinterpret_cast<const uint8_t*>(&message);
        int offset = find_options_start(message, 548); // sizeof(DHCPMessage) = 548
        if (offset == -1) {
            return false;
        }
        int option_index = offset + 4; // Skip magic cookie
        while (option_index < 548) {
            if (option_index >= 548) break;
            uint8_t option_code = raw_data[option_index++];
            if (option_code == 0) continue;
            if (option_code == 255) break;
            if (option_index >= 548) {
                std::cerr << "Option length byte missing." << std::endl;
                return false;
            }
            uint8_t option_length = raw_data[option_index++];
            if (option_index + option_length > 548) {
                std::cerr << "Invalid option length." << std::endl;
                return false;
            }
            if (option_code == 50) { // Requested IP Address
                if (option_length == 4) {
                    memcpy(&requested_ip, &raw_data[option_index], 4);
                    return true;
                } else {
                    std::cerr << "Invalid option length for option 50." << std::endl;
                    return false;
                }
            }
            option_index += option_length;
        }
        return false;
    }

    void add_dhcp_options(DHCPMessage& response, in_addr_t offered_ip, bool is_inform = false) {
        uint8_t subnet_mask_bytes[4];
        uint8_t router_bytes[4];
        uint8_t dns_bytes[4];

        inet_pton(AF_INET, subnet_mask_.c_str(), subnet_mask_bytes);
        inet_pton(AF_INET, router_.c_str(), router_bytes);
        inet_pton(AF_INET, dns_.c_str(), dns_bytes);

        int options_start = 4;

        options_start = add_option(response, 1, subnet_mask_bytes, 4, options_start);   // Subnet Mask
        options_start = add_option(response, 3, router_bytes, 4, options_start);      // Router
        options_start = add_option(response, 6, dns_bytes, 4, options_start);         // DNS Server

        if (!is_inform) {
            uint32_t lease_time_network = htonl(lease_time_);
            options_start = add_option(response, 51, reinterpret_cast<uint8_t*>(&lease_time_network), 4, options_start); // Lease Time
        }

        uint8_t server_ip_bytes[4];
        in_addr server_ip = get_server_ip();
        memcpy(server_ip_bytes, &server_ip.s_addr, 4);
        options_start = add_option(response, 54, server_ip_bytes, 4, options_start); // DHCP Server Identifier

        add_option(response, 255, nullptr, 0, options_start); // End option
    }

    int add_option(DHCPMessage& response, uint8_t code, const uint8_t* data, int len, int offset) {
        if (offset + 2 + len > sizeof(response.options)) {
            std::cerr << "DHCP options buffer overflow!" << std::endl;
            return offset;
        }
        response.options[offset++] = code;
        if (len > 0) {
            response.options[offset++] = len;
            memcpy(&response.options[offset], data, len);
            offset += len;
        }
        return offset;
    }

    void send_dhcp_response(const DHCPMessage& request, const DHCPMessage& response, bool unicast = false) {
        struct sockaddr_in destination_addr;
        memset(&destination_addr, 0, sizeof(destination_addr));
        destination_addr.sin_family = AF_INET;
    
        if (request.ciaddr.s_addr != 0 && unicast) {
            destination_addr.sin_port = htons(DHCP_CLIENT_PORT);
            destination_addr.sin_addr = request.ciaddr;
        } else if ((request.flags & (1 << 15)) || request.ciaddr.s_addr == 0) {
            destination_addr.sin_port = htons(DHCP_CLIENT_PORT);
            destination_addr.sin_addr.s_addr = INADDR_BROADCAST;
        } else {
            destination_addr.sin_port = htons(DHCP_CLIENT_PORT);
            destination_addr.sin_addr = response.yiaddr;
        }
    
        uint8_t message_type = get_dhcp_message_type(response, sizeof(response));
        std::cout << "Sending DHCP response (type " << (int)message_type << ") to "
                  << mac_to_string(response.chaddr, response.hlen) << " with IP "
                  << inet_ntoa(response.yiaddr) << std::endl;
    
        ssize_t sent_len = sendto(sockfd_, &response, sizeof(response), 0,
                                  (const struct sockaddr *)&destination_addr,
                                  sizeof(destination_addr));
        if (sent_len < 0) {
            perror("sendto failed");
        } else {
            std::cout << "Sent " << sent_len << " bytes" << std::endl;
        }
    }

    int find_options_start(const DHCPMessage& message, ssize_t recv_len) {
        const uint8_t* raw_data = reinterpret_cast<const uint8_t*>(&message);
        int offset = 0;
        offset += sizeof(message.op);      // 1
        offset += sizeof(message.htype);   // 1
        offset += sizeof(message.hlen);    // 1
        offset += sizeof(message.hops);    // 1
        offset += sizeof(message.xid);     // 4
        offset += sizeof(message.secs);    // 2
        offset += sizeof(message.flags);   // 2
        offset += sizeof(message.ciaddr);  // 4
        offset += sizeof(message.yiaddr);  // 4
        offset += sizeof(message.siaddr);  // 4
        offset += sizeof(message.giaddr);  // 4
        offset += sizeof(message.chaddr);  // 16
        offset += sizeof(message.sname);   // 64
        offset += sizeof(message.file);    // 128
        // Total: 1+1+1+1+4+2+2+4+4+4+4+16+64+128 = 236

        std::cout << "Calculated options offset: " << offset << std::endl;

        if (offset + 4 > recv_len) {
            std::cerr << "Not enough space for magic cookie." << std::endl;
            return -1;
        }

        std::cout << "Checking magic cookie at offset: " << offset << std::endl;
        std::cout << "Bytes at offset: "
                  << std::hex
                  << (int)raw_data[offset] << " "
                  << (int)raw_data[offset + 1] << " "
                  << (int)raw_data[offset + 2] << " "
                  << (int)raw_data[offset + 3] << " "
                  << std::dec << std::endl;

        if (raw_data[offset] == 99 &&
            raw_data[offset + 1] == 130 &&
            raw_data[offset + 2] == 83 &&
            raw_data[offset + 3] == 99) {
            std::cout << "Magic cookie found!" << std::endl;
            return offset;
        }

        std::cerr << "Magic cookie not found." << std::endl;
        return -1;
    }

    uint8_t get_dhcp_message_type(const DHCPMessage& message, ssize_t message_size) {
        const uint8_t* raw_data = reinterpret_cast<const uint8_t*>(&message);
        int offset = find_options_start(message, message_size);
        if (offset == -1) {
            return 0;
        }
        int option_index = offset + 4; // Skip magic cookie
        while (option_index < message_size) {
            if (option_index >= message_size) {
                std::cerr << "Option code byte missing." << std::endl;
                break;
            }
            uint8_t option_code = raw_data[option_index++];
            if (option_code == 0) continue;
            if (option_code == 255) break;
            if (option_index >= message_size) {
                std::cerr << "Option length byte missing." << std::endl;
                return 0;
            }
            uint8_t option_length = raw_data[option_index++];
            if (option_index + option_length > message_size) {
                std::cerr << "Invalid option length: " << (int)option_length
                          << " at index: " << option_index - 2
                          << ". Remaining bytes: " << message_size - option_index << std::endl;
                return 0;
            }
            if (option_code == 53) {
                if (option_length == 1) {
                    uint8_t message_type = raw_data[option_index];
                    std::cout << "DHCP Message Type FOUND: " << (int)message_type << std::endl;
                    return message_type;
                } else {
                    std::cerr << "Invalid option length for option 53" << std::endl;
                    return 0;
                }
            }
            option_index += option_length;
        }
        std::cerr << "DHCP Message Type (option 53) not found." << std::endl;
        return 0;
    }

    std::string mac_to_string(const uint8_t* mac, uint8_t len) {
        char mac_str[18];
        if (len != 6) {
            return "Invalid MAC";
        }
        snprintf(mac_str, sizeof(mac_str), "%02x:%02x:%02x:%02x:%02x:%02x",
                 mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
        return mac_str;
    }

    in_addr get_server_ip() {
        struct ifaddrs *ifaddr, *ifa;
        in_addr server_ip;
        server_ip.s_addr = INADDR_ANY;

        if (getifaddrs(&ifaddr) == -1) {
            perror("getifaddrs");
            return server_ip;
        }

        for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
            if (ifa->ifa_addr == NULL) continue;
            if (ifa->ifa_addr->sa_family == AF_INET && !(ifa->ifa_flags & IFF_LOOPBACK)) {
                server_ip = ((struct sockaddr_in *)ifa->ifa_addr)->sin_addr;
                break;
            }
        }

        freeifaddrs(ifaddr);
        return server_ip;
    }

    void load_leases() {
        std::ifstream file("dhcp_leases.txt");
        if (!file.is_open()) {
            std::cout << "No existing lease file found." << std::endl;
            return;
        }
        std::string line;
        while (std::getline(file, line)) {
            std::istringstream iss(line);
            std::string mac_str, ip_str;
            time_t expiry;
            int declined_int;

            if (!(iss >> mac_str >> ip_str >> expiry >> declined_int)) {
                std::cerr << "Error parsing lease file line: " << line << std::endl;
                continue;
            }

            Lease lease;
            lease.ip_address.s_addr = inet_addr(ip_str.c_str());
            lease.expiry_time = expiry;
            lease.declined = (declined_int != 0);

            leases_[mac_str] = lease;
        }
        file.close();
        std::cout << "Loaded leases from dhcp_leases.txt" << std::endl;
    }

    void save_leases() {
        std::ofstream file("dhcp_leases.txt");
        if (!file.is_open()) {
            std::cerr << "Error opening lease file for writing." << std::endl;
            return;
        }
        for (const auto& pair : leases_) {
            file << pair.first << " "
                 << inet_ntoa(pair.second.ip_address) << " "
                 << pair.second.expiry_time << " "
                 << (pair.second.declined ? 1 : 0) << std::endl;
        }
        file.close();
        std::cout << "Saved leases to dhcp_leases.txt" << std::endl;
    }
};

int main() {
    try {
        DHCPServer server("172.20.0.100", "172.20.0.200", "255.255.0.0", "172.20.0.1", "8.8.8.8", 3600);

        signal(SIGINT, signalHandler);
        signal(SIGTERM, signalHandler);

        std::thread server_thread(&DHCPServer::run, &server);

        while (keepRunning) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

        server.stop();
        server_thread.join();

    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}