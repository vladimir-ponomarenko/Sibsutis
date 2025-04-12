#include <arpa/inet.h>
#include <ifaddrs.h>
#include <net/if.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <algorithm>
#include <atomic>
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <thread>
#include <vector>

#define DHCP_SERVER_PORT 67
#define DHCP_CLIENT_PORT 68
#define BOOTREQUEST 1
#define BOOTREPLY 2

#define DHCPDISCOVER 1
#define DHCPOFFER 2
#define DHCPREQUEST 3
#define DHCPDECLINE 4
#define DHCPACK 5
#define DHCPNAK 6
#define DHCPRELEASE 7
#define DHCPINFORM 8

#define OPTION_PAD 0
#define OPTION_SUBNET_MASK 1
#define OPTION_ROUTER 3
#define OPTION_DNS_SERVER 6
#define OPTION_REQUESTED_IP 50
#define OPTION_LEASE_TIME 51
#define OPTION_DHCP_MESSAGE_TYPE 53
#define OPTION_SERVER_IDENTIFIER 54
#define OPTION_PARAMETER_REQUEST_LIST 55
#define OPTION_END 255

#define DHCP_FIXED_HEADER_SIZE 236
#define DHCP_OPTIONS_BUFFER_SIZE 312
#define MAX_DHCP_PACKET_SIZE (DHCP_FIXED_HEADER_SIZE + DHCP_OPTIONS_BUFFER_SIZE)

struct DHCPFixedHeader {
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
    DHCPServer(const std::string& ip_range_start,
               const std::string& ip_range_end, const std::string& subnet_mask,
               const std::string& router, const std::string& dns,
               int lease_time)
        : ip_range_start_str_(ip_range_start),
          ip_range_end_str_(ip_range_end),
          subnet_mask_str_(subnet_mask),
          router_str_(router),
          dns_str_(dns),
          lease_time_(lease_time),
          sockfd_(-1) {
        if (!parse_ip_range()) {
            throw std::runtime_error("Invalid IP range.");
        }

        if (inet_pton(AF_INET, subnet_mask_str_.c_str(), &subnet_mask_) != 1) {
            throw std::runtime_error("Invalid subnet mask format.");
        }
        if (inet_pton(AF_INET, router_str_.c_str(), &router_) != 1) {
            throw std::runtime_error("Invalid router IP format.");
        }
        if (inet_pton(AF_INET, dns_str_.c_str(), &dns_) != 1) {
            throw std::runtime_error("Invalid DNS IP format.");
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

        std::cout << "DHCP Server started. Listening on port "
                  << DHCP_SERVER_PORT << std::endl;

        while (keepRunning) {
            receive_message();
        }
        std::cout << "DHCP Server shutting down." << std::endl;
    }

    void stop() { keepRunning = false; }

   private:
    int sockfd_;
    struct sockaddr_in server_addr_, client_addr_;
    std::string ip_range_start_str_;
    std::string ip_range_end_str_;
    std::string subnet_mask_str_;
    std::string router_str_;
    std::string dns_str_;

    in_addr_t ip_start_n_;
    in_addr_t ip_end_n_;
    uint8_t subnet_mask_[4];
    uint8_t router_[4];
    uint8_t dns_[4];
    int lease_time_;
    std::map<std::string, Lease> leases_;

    bool parse_ip_range() {
        struct in_addr start_addr, end_addr;
        if (inet_pton(AF_INET, ip_range_start_str_.c_str(), &start_addr) != 1 ||
            inet_pton(AF_INET, ip_range_end_str_.c_str(), &end_addr) != 1) {
            return false;
        }

        ip_start_n_ = ntohl(start_addr.s_addr);
        ip_end_n_ = ntohl(end_addr.s_addr);
        return (ip_start_n_ != INADDR_NONE && ip_end_n_ != INADDR_NONE &&
                ip_start_n_ <= ip_end_n_);
    }

    bool create_socket() {
        sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
        if (sockfd_ < 0) {
            perror("socket creation failed");
            return false;
        }

        int reuse = 1;
        if (setsockopt(sockfd_, SOL_SOCKET, SO_REUSEADDR, &reuse,
                       sizeof(reuse)) < 0) {
            perror("setsockopt(SO_REUSEADDR) failed");
        }

        memset(&server_addr_, 0, sizeof(server_addr_));
        memset(&client_addr_, 0, sizeof(client_addr_));

        server_addr_.sin_family = AF_INET;
        server_addr_.sin_addr.s_addr = INADDR_ANY;
        server_addr_.sin_port = htons(DHCP_SERVER_PORT);

        int broadcast_enable = 1;
        if (setsockopt(sockfd_, SOL_SOCKET, SO_BROADCAST, &broadcast_enable,
                       sizeof(broadcast_enable)) < 0) {
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

        if (bind(sockfd_, (const struct sockaddr*)&server_addr_,
                 sizeof(server_addr_)) < 0) {
            perror("bind failed");
            close(sockfd_);
            return false;
        }
        return true;
    }

    void receive_message() {
        uint8_t buffer[MAX_DHCP_PACKET_SIZE];
        socklen_t client_addr_len = sizeof(client_addr_);
        memset(buffer, 0, sizeof(buffer));

        ssize_t recv_len =
            recvfrom(sockfd_, buffer, sizeof(buffer), 0,
                     (struct sockaddr*)&client_addr_, &client_addr_len);

        if (recv_len < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                return;
            }

            return;
        }

        if (recv_len < DHCP_FIXED_HEADER_SIZE) {
            std::cerr << "Received packet is too small (" << recv_len
                      << " bytes)." << std::endl;
            return;
        }

        DHCPFixedHeader request_header;
        memcpy(&request_header, buffer, DHCP_FIXED_HEADER_SIZE);

        if (request_header.op != BOOTREQUEST) {
            return;
        }

        std::string client_mac =
            mac_to_string(request_header.chaddr, request_header.hlen);
        if (client_mac == "Invalid MAC") {
            std::cerr << "Received invalid MAC length: "
                      << (int)request_header.hlen << std::endl;
            return;
        }
        std::cout << "Received message from: " << client_mac << " (" << recv_len
                  << " bytes)" << std::endl;

        uint8_t message_type = get_dhcp_option_value_byte(
            buffer, recv_len, OPTION_DHCP_MESSAGE_TYPE);

        uint8_t response_buffer[MAX_DHCP_PACKET_SIZE];
        memset(response_buffer, 0, sizeof(response_buffer));
        DHCPFixedHeader* response_header =
            reinterpret_cast<DHCPFixedHeader*>(response_buffer);
        int options_len = 0;

        switch (message_type) {
            case DHCPDISCOVER:
                std::cout << "  Message Type: DHCPDISCOVER" << std::endl;
                options_len = handle_dhcp_discover(request_header, buffer,
                                                   recv_len, *response_header);
                break;
            case DHCPREQUEST:
                std::cout << "  Message Type: DHCPREQUEST" << std::endl;
                options_len = handle_dhcp_request(request_header, buffer,
                                                  recv_len, *response_header);
                break;
            case DHCPDECLINE:
                std::cout << "  Message Type: DHCPDECLINE" << std::endl;
                handle_dhcp_decline(request_header, buffer, recv_len);
                options_len = 0;
                break;
            case DHCPRELEASE:
                std::cout << "  Message Type: DHCPRELEASE" << std::endl;
                handle_dhcp_release(request_header);
                options_len = 0;
                break;
            case DHCPINFORM:
                std::cout << "  Message Type: DHCPINFORM" << std::endl;
                options_len = handle_dhcp_inform(request_header, buffer,
                                                 recv_len, *response_header);
                break;
            default:
                std::cout
                    << "  Unknown or missing DHCP message type (Option 53): "
                    << (int)message_type << std::endl;
                options_len = 0;
        }

        if (options_len > 0) {
            send_dhcp_response(request_header, response_buffer,
                               DHCP_FIXED_HEADER_SIZE + options_len);
        }
    }

    int handle_dhcp_discover(const DHCPFixedHeader& request_header,
                             const uint8_t* request_buffer, ssize_t request_len,
                             DHCPFixedHeader& response_header) {
        int options_offset = 0;

        prepare_dhcp_response_header(request_header, response_header);
        options_offset =
            add_magic_cookie(reinterpret_cast<uint8_t*>(&response_header) +
                             DHCP_FIXED_HEADER_SIZE);

        options_offset =
            add_option(response_header, OPTION_DHCP_MESSAGE_TYPE,
                       static_cast<uint8_t>(DHCPOFFER),
                       reinterpret_cast<uint8_t*>(&response_header) +
                           DHCP_FIXED_HEADER_SIZE,
                       options_offset);

        in_addr offered_ip_addr;
        in_addr requested_ip_addr =
            get_requested_ip(request_buffer, request_len);

        in_addr_t offered_ip_h = find_or_allocate_ip(
            request_header, requested_ip_addr, offered_ip_addr);

        if (offered_ip_h == INADDR_NONE) {
            std::cerr << "No available IP addresses for "
                      << mac_to_string(request_header.chaddr,
                                       request_header.hlen)
                      << std::endl;

            return 0;
        }

        response_header.yiaddr = offered_ip_addr;

        options_offset =
            add_standard_options(response_header, offered_ip_h,
                                 reinterpret_cast<uint8_t*>(&response_header) +
                                     DHCP_FIXED_HEADER_SIZE,
                                 options_offset);
        options_offset =
            add_option(response_header, OPTION_END, static_cast<uint8_t>(0),
                       reinterpret_cast<uint8_t*>(&response_header) +
                           DHCP_FIXED_HEADER_SIZE,
                       options_offset);

        return options_offset;
    }

    int handle_dhcp_request(const DHCPFixedHeader& request_header,
                            const uint8_t* request_buffer, ssize_t request_len,
                            DHCPFixedHeader& response_header) {
        int options_offset = 0;
        std::string client_mac =
            mac_to_string(request_header.chaddr, request_header.hlen);
        in_addr requested_ip_addr =
            get_requested_ip(request_buffer, request_len);
        in_addr server_id_addr =
            get_server_id_from_options(request_buffer, request_len);
        in_addr client_current_ip = request_header.ciaddr;

        in_addr my_server_ip = get_server_ip();
        if (server_id_addr.s_addr != 0 &&
            server_id_addr.s_addr != my_server_ip.s_addr) {
            std::cout << "  Request is for another server ("
                      << inet_ntoa(server_id_addr) << "), ignoring."
                      << std::endl;
            return 0;
        }

        in_addr target_ip_addr = {0};
        if (client_current_ip.s_addr != 0) {
            target_ip_addr = client_current_ip;
            std::cout << "  Client " << client_mac
                      << " is renewing/rebinding IP "
                      << inet_ntoa(target_ip_addr) << std::endl;
        } else if (requested_ip_addr.s_addr != 0) {
            target_ip_addr = requested_ip_addr;
            std::cout << "  Client " << client_mac << " selected offer for IP "
                      << inet_ntoa(target_ip_addr) << std::endl;
        } else {
            std::cerr << "  DHCPREQUEST from " << client_mac
                      << " without ciaddr or requested IP. Sending NAK."
                      << std::endl;
            prepare_dhcp_response_header(request_header, response_header);
            options_offset =
                add_magic_cookie(reinterpret_cast<uint8_t*>(&response_header) +
                                 DHCP_FIXED_HEADER_SIZE);

            options_offset =
                add_option(response_header, OPTION_DHCP_MESSAGE_TYPE,
                           static_cast<uint8_t>(DHCPNAK),
                           reinterpret_cast<uint8_t*>(&response_header) +
                               DHCP_FIXED_HEADER_SIZE,
                           options_offset);
            options_offset = add_option(
                response_header, OPTION_SERVER_IDENTIFIER, my_server_ip.s_addr,
                reinterpret_cast<uint8_t*>(&response_header) +
                    DHCP_FIXED_HEADER_SIZE,
                options_offset);
            options_offset =
                add_option(response_header, OPTION_END, static_cast<uint8_t>(0),
                           reinterpret_cast<uint8_t*>(&response_header) +
                               DHCP_FIXED_HEADER_SIZE,
                           options_offset);
            return options_offset;
        }

        auto lease_it = leases_.find(client_mac);
        bool can_assign = false;

        if (lease_it != leases_.end()) {
            if (lease_it->second.ip_address.s_addr == target_ip_addr.s_addr &&
                !lease_it->second.declined) {
                lease_it->second.expiry_time = time(nullptr) + lease_time_;
                lease_it->second.declined = false;
                can_assign = true;
                std::cout << "  Renewed lease for " << inet_ntoa(target_ip_addr)
                          << " to " << client_mac << std::endl;
            } else {
                if (is_ip_available(ntohl(target_ip_addr.s_addr))) {
                    leases_[client_mac] = {target_ip_addr,
                                           time(nullptr) + lease_time_, false};
                    can_assign = true;
                    std::cout << "  Assigned new/declined IP "
                              << inet_ntoa(target_ip_addr) << " to "
                              << client_mac << std::endl;
                }
            }
        } else {
            if (is_ip_available(ntohl(target_ip_addr.s_addr))) {
                leases_[client_mac] = {target_ip_addr,
                                       time(nullptr) + lease_time_, false};
                can_assign = true;
                std::cout << "  Assigned IP " << inet_ntoa(target_ip_addr)
                          << " to " << client_mac << " (new lease)"
                          << std::endl;
            }
        }

        prepare_dhcp_response_header(request_header, response_header);
        options_offset =
            add_magic_cookie(reinterpret_cast<uint8_t*>(&response_header) +
                             DHCP_FIXED_HEADER_SIZE);

        if (can_assign) {
            response_header.yiaddr = target_ip_addr;

            options_offset =
                add_option(response_header, OPTION_DHCP_MESSAGE_TYPE,
                           static_cast<uint8_t>(DHCPACK),
                           reinterpret_cast<uint8_t*>(&response_header) +
                               DHCP_FIXED_HEADER_SIZE,
                           options_offset);
            options_offset = add_standard_options(
                response_header, ntohl(target_ip_addr.s_addr),
                reinterpret_cast<uint8_t*>(&response_header) +
                    DHCP_FIXED_HEADER_SIZE,
                options_offset);
        } else {
            std::cerr << "  Cannot assign requested/current IP "
                      << inet_ntoa(target_ip_addr) << " to " << client_mac
                      << ". Sending NAK." << std::endl;

            options_offset =
                add_option(response_header, OPTION_DHCP_MESSAGE_TYPE,
                           static_cast<uint8_t>(DHCPNAK),
                           reinterpret_cast<uint8_t*>(&response_header) +
                               DHCP_FIXED_HEADER_SIZE,
                           options_offset);
            options_offset = add_option(
                response_header, OPTION_SERVER_IDENTIFIER, my_server_ip.s_addr,
                reinterpret_cast<uint8_t*>(&response_header) +
                    DHCP_FIXED_HEADER_SIZE,
                options_offset);
        }

        options_offset =
            add_option(response_header, OPTION_END, static_cast<uint8_t>(0),
                       reinterpret_cast<uint8_t*>(&response_header) +
                           DHCP_FIXED_HEADER_SIZE,
                       options_offset);
        return options_offset;
    }

    int handle_dhcp_inform(const DHCPFixedHeader& request_header,
                           const uint8_t* request_buffer, ssize_t request_len,
                           DHCPFixedHeader& response_header) {
        int options_offset = 0;
        std::cout << "  Processing DHCPINFORM from "
                  << mac_to_string(request_header.chaddr, request_header.hlen)
                  << " with IP " << inet_ntoa(request_header.ciaddr)
                  << std::endl;

        prepare_dhcp_response_header(request_header, response_header);

        response_header.yiaddr.s_addr = 0;

        response_header.ciaddr = request_header.ciaddr;

        options_offset =
            add_magic_cookie(reinterpret_cast<uint8_t*>(&response_header) +
                             DHCP_FIXED_HEADER_SIZE);

        options_offset =
            add_option(response_header, OPTION_DHCP_MESSAGE_TYPE,
                       static_cast<uint8_t>(DHCPACK),
                       reinterpret_cast<uint8_t*>(&response_header) +
                           DHCP_FIXED_HEADER_SIZE,
                       options_offset);

        options_offset =
            add_standard_options(response_header, 0,
                                 reinterpret_cast<uint8_t*>(&response_header) +
                                     DHCP_FIXED_HEADER_SIZE,
                                 options_offset, true);

        options_offset =
            add_option(response_header, OPTION_END, static_cast<uint8_t>(0),
                       reinterpret_cast<uint8_t*>(&response_header) +
                           DHCP_FIXED_HEADER_SIZE,
                       options_offset);

        return options_offset;
    }

    void handle_dhcp_decline(const DHCPFixedHeader& request_header,
                             const uint8_t* request_buffer,
                             ssize_t request_len) {
        std::string client_mac =
            mac_to_string(request_header.chaddr, request_header.hlen);

        in_addr declined_ip_addr =
            get_requested_ip(request_buffer, request_len);

        auto it = leases_.find(client_mac);
        if (it != leases_.end()) {
            if (declined_ip_addr.s_addr != 0 &&
                it->second.ip_address.s_addr != declined_ip_addr.s_addr) {
                std::cout << "  DHCPDECLINE from " << client_mac << " for IP "
                          << inet_ntoa(declined_ip_addr)
                          << ", but current lease is for "
                          << inet_ntoa(it->second.ip_address)
                          << ". Marking lease as declined anyway." << std::endl;
            } else {
                std::cout << "  Marked IP " << inet_ntoa(it->second.ip_address)
                          << " as declined by " << client_mac << std::endl;
            }
            it->second.declined = true;
            it->second.expiry_time = time(nullptr) + 60;
        } else if (declined_ip_addr.s_addr != 0) {
            for (auto& pair : leases_) {
                if (pair.second.ip_address.s_addr == declined_ip_addr.s_addr) {
                    std::cout
                        << "  Marked IP " << inet_ntoa(pair.second.ip_address)
                        << " as declined by " << client_mac << " (found by IP)."
                        << std::endl;
                    pair.second.declined = true;
                    pair.second.expiry_time = time(nullptr) + 60;
                    break;
                }
            }
        } else {
            std::cout << "  Received DHCPDECLINE from " << client_mac
                      << " without specific IP or existing lease." << std::endl;
        }
    }

    void handle_dhcp_release(const DHCPFixedHeader& request_header) {
        std::string client_mac =
            mac_to_string(request_header.chaddr, request_header.hlen);
        in_addr client_ip = request_header.ciaddr;

        auto it = leases_.find(client_mac);
        if (it != leases_.end()) {
            if (it->second.ip_address.s_addr == client_ip.s_addr) {
                std::cout << "  Released IP "
                          << inet_ntoa(it->second.ip_address) << " from "
                          << client_mac << std::endl;
                leases_.erase(it);
            } else {
                std::cout << "  Received DHCPRELEASE from " << client_mac
                          << " for IP " << inet_ntoa(client_ip)
                          << ", but current lease is for "
                          << inet_ntoa(it->second.ip_address) << ". Ignoring."
                          << std::endl;
            }
        } else {
            std::cout << "  Received DHCPRELEASE from " << client_mac
                      << " with IP " << inet_ntoa(client_ip)
                      << ", but no lease found. Ignoring." << std::endl;
        }
    }

    void prepare_dhcp_response_header(const DHCPFixedHeader& request_header,
                                      DHCPFixedHeader& response_header) {
        response_header.op = BOOTREPLY;
        response_header.htype = request_header.htype;
        response_header.hlen = request_header.hlen;
        response_header.hops = 0;
        response_header.xid = request_header.xid;
        response_header.secs = 0;
        response_header.flags = request_header.flags;
        response_header.ciaddr.s_addr = 0;
        response_header.yiaddr.s_addr = 0;
        response_header.siaddr = get_server_ip();
        response_header.giaddr = request_header.giaddr;

        if (request_header.hlen <= 16) {
            memcpy(response_header.chaddr, request_header.chaddr,
                   request_header.hlen);
        } else {
            memcpy(response_header.chaddr, request_header.chaddr, 16);
        }
        memset(response_header.sname, 0, sizeof(response_header.sname));
        memset(response_header.file, 0, sizeof(response_header.file));
    }

    in_addr_t find_or_allocate_ip(const DHCPFixedHeader& request_header,
                                  const in_addr& requested_ip_addr,
                                  in_addr& offered_ip_addr) {
        std::string client_mac =
            mac_to_string(request_header.chaddr, request_header.hlen);

        auto lease_it = leases_.find(client_mac);
        if (lease_it != leases_.end() &&
            lease_it->second.expiry_time > time(nullptr) &&
            !lease_it->second.declined) {
            offered_ip_addr = lease_it->second.ip_address;
            std::cout << "  Offering existing lease IP "
                      << inet_ntoa(offered_ip_addr) << " to " << client_mac
                      << std::endl;
            return ntohl(offered_ip_addr.s_addr);
        }

        if (requested_ip_addr.s_addr != 0) {
            in_addr_t requested_ip_h = ntohl(requested_ip_addr.s_addr);
            if (is_ip_available(requested_ip_h)) {
                offered_ip_addr = requested_ip_addr;
                std::cout << "  Offering requested IP "
                          << inet_ntoa(offered_ip_addr) << " to " << client_mac
                          << std::endl;
                return requested_ip_h;
            } else {
                std::cout << "  Requested IP " << inet_ntoa(requested_ip_addr)
                          << " by " << client_mac << " is not available."
                          << std::endl;
            }
        }

        if (lease_it != leases_.end()) {
            in_addr_t old_ip_h = ntohl(lease_it->second.ip_address.s_addr);
            if (is_ip_available(old_ip_h)) {
                offered_ip_addr = lease_it->second.ip_address;
                std::cout << "  Re-offering expired/declined IP "
                          << inet_ntoa(offered_ip_addr) << " to " << client_mac
                          << std::endl;
                return old_ip_h;
            }
        }

        for (in_addr_t current_ip_h = ip_start_n_; current_ip_h <= ip_end_n_;
             ++current_ip_h) {
            if (is_ip_available(current_ip_h)) {
                offered_ip_addr.s_addr = htonl(current_ip_h);
                std::cout << "  Offering new IP " << inet_ntoa(offered_ip_addr)
                          << " to " << client_mac << std::endl;
                return current_ip_h;
            }
        }

        offered_ip_addr.s_addr = 0;
        return INADDR_NONE;
    }

    bool is_ip_available(in_addr_t ip_h) {
        if (ip_h < ip_start_n_ || ip_h > ip_end_n_) {
            return false;
        }

        for (const auto& pair : leases_) {
            if (ntohl(pair.second.ip_address.s_addr) == ip_h &&
                pair.second.expiry_time > time(nullptr) &&
                !pair.second.declined) {
                return false;
            }
        }
        return true;
    }

    in_addr get_requested_ip(const uint8_t* buffer, ssize_t buffer_len) {
        in_addr requested_ip = {0};
        get_dhcp_option_value(buffer, buffer_len, OPTION_REQUESTED_IP,
                              reinterpret_cast<uint8_t*>(&requested_ip.s_addr),
                              sizeof(requested_ip.s_addr));
        return requested_ip;
    }

    in_addr get_server_id_from_options(const uint8_t* buffer,
                                       ssize_t buffer_len) {
        in_addr server_id = {0};
        get_dhcp_option_value(buffer, buffer_len, OPTION_SERVER_IDENTIFIER,
                              reinterpret_cast<uint8_t*>(&server_id.s_addr),
                              sizeof(server_id.s_addr));
        return server_id;
    }

    int add_standard_options(DHCPFixedHeader& response_header,
                             in_addr_t offered_ip_h, uint8_t* options_buffer,
                             int current_offset, bool is_inform = false) {
        current_offset =
            add_option(response_header, OPTION_SUBNET_MASK, subnet_mask_,
                       options_buffer, current_offset);
        current_offset = add_option(response_header, OPTION_ROUTER, router_,
                                    options_buffer, current_offset);
        current_offset = add_option(response_header, OPTION_DNS_SERVER, dns_,
                                    options_buffer, current_offset);

        if (!is_inform) {
            uint32_t lease_time_nbo = htonl(lease_time_);
            current_offset =
                add_option(response_header, OPTION_LEASE_TIME, lease_time_nbo,
                           options_buffer, current_offset);
        }

        in_addr server_ip = get_server_ip();
        current_offset =
            add_option(response_header, OPTION_SERVER_IDENTIFIER,
                       server_ip.s_addr, options_buffer, current_offset);

        return current_offset;
    }

    int add_magic_cookie(uint8_t* options_buffer) {
        if (DHCP_OPTIONS_BUFFER_SIZE < 4) return 0;
        options_buffer[0] = 99;
        options_buffer[1] = 130;
        options_buffer[2] = 83;
        options_buffer[3] = 99;
        return 4;
    }

    int add_option(DHCPFixedHeader& response_header, uint8_t code,
                   uint32_t data_nbo, uint8_t* options_buffer, int offset) {
        if (code == OPTION_SUBNET_MASK || code == OPTION_ROUTER ||
            code == OPTION_DNS_SERVER || code == OPTION_SERVER_IDENTIFIER ||
            code == OPTION_LEASE_TIME || code == OPTION_REQUESTED_IP) {
            return add_option_raw(options_buffer, offset, code,
                                  reinterpret_cast<const uint8_t*>(&data_nbo),
                                  4);
        }

        std::cerr << "Warning: Unsupported option code " << (int)code
                  << " in add_option(uint32_t)" << std::endl;
        return offset;
    }

    int add_option(DHCPFixedHeader& response_header, uint8_t code,
                   uint8_t data_byte, uint8_t* options_buffer, int offset) {
        if (code == OPTION_DHCP_MESSAGE_TYPE || code == OPTION_END ||
            code == OPTION_PAD) {
            return add_option_raw(
                options_buffer, offset, code, &data_byte,
                (code == OPTION_END || code == OPTION_PAD) ? 0 : 1);
        }
        std::cerr << "Warning: Unsupported option code " << (int)code
                  << " in add_option(uint8_t)" << std::endl;
        return offset;
    }

    int add_option(DHCPFixedHeader& response_header, uint8_t code,
                   const uint8_t* data_array, uint8_t* options_buffer,
                   int offset) {
        if (code == OPTION_SUBNET_MASK || code == OPTION_ROUTER ||
            code == OPTION_DNS_SERVER) {
            return add_option_raw(options_buffer, offset, code, data_array, 4);
        }
        std::cerr << "Warning: Unsupported option code " << (int)code
                  << " in add_option(uint8_t*)" << std::endl;
        return offset;
    }

    int add_option_raw(uint8_t* options_buffer, int offset, uint8_t code,
                       const uint8_t* data, uint8_t len) {
        int required_space =
            (code == OPTION_END || code == OPTION_PAD) ? 1 : (2 + len);
        if (offset + required_space > DHCP_OPTIONS_BUFFER_SIZE) {
            std::cerr << "DHCP options buffer overflow! Cannot add option "
                      << (int)code << std::endl;
            return offset;
        }

        options_buffer[offset++] = code;

        if (code != OPTION_END && code != OPTION_PAD) {
            options_buffer[offset++] = len;
            if (len > 0 && data != nullptr) {
                memcpy(&options_buffer[offset], data, len);
                offset += len;
            }
        }
        return offset;
    }

    void send_dhcp_response(const DHCPFixedHeader& request_header,
                            const uint8_t* response_buffer,
                            size_t response_len) {
        struct sockaddr_in destination_addr;
        memset(&destination_addr, 0, sizeof(destination_addr));
        destination_addr.sin_family = AF_INET;
        destination_addr.sin_port = htons(DHCP_CLIENT_PORT);

        const DHCPFixedHeader* response_header =
            reinterpret_cast<const DHCPFixedHeader*>(response_buffer);

        if (request_header.ciaddr.s_addr == 0) {
            if (request_header.flags & htons(0x8000)) {
                destination_addr.sin_addr.s_addr = INADDR_BROADCAST;
                std::cout
                    << "  Sending response via BROADCAST (ciaddr=0, B-flag=1)"
                    << std::endl;
            } else {
                if (request_header.giaddr.s_addr != 0) {
                    destination_addr.sin_addr = request_header.giaddr;

                    destination_addr.sin_port = htons(DHCP_SERVER_PORT);
                    std::cout
                        << "  Sending response via UNICAST to Relay Agent "
                        << inet_ntoa(destination_addr.sin_addr) << ":"
                        << ntohs(destination_addr.sin_port) << std::endl;
                } else {
                    destination_addr.sin_addr.s_addr = INADDR_BROADCAST;
                    std::cout << "  Sending response via BROADCAST (ciaddr=0, "
                                 "B-flag=0, no giaddr)"
                              << std::endl;
                }
            }
        } else {
            destination_addr.sin_addr = request_header.ciaddr;
            std::cout << "  Sending response via UNICAST to ciaddr "
                      << inet_ntoa(destination_addr.sin_addr) << std::endl;
        }

        ssize_t sent_len = sendto(sockfd_, response_buffer, response_len, 0,
                                  (const struct sockaddr*)&destination_addr,
                                  sizeof(destination_addr));

        if (sent_len < 0) {
            perror("sendto failed");
        } else if (sent_len != response_len) {
            std::cerr << "Warning: sent " << sent_len
                      << " bytes, but expected to send " << response_len
                      << std::endl;
        } else {
            std::cout << "  Sent " << sent_len << " bytes response."
                      << std::endl;
        }
    }

    bool get_dhcp_option_value(const uint8_t* buffer, ssize_t buffer_len,
                               uint8_t option_code_to_find, uint8_t* value_out,
                               uint8_t max_value_len) {
        if (buffer_len <= DHCP_FIXED_HEADER_SIZE + 4) {
            return false;
        }

        const uint8_t* options_start = buffer + DHCP_FIXED_HEADER_SIZE;
        ssize_t options_total_len = buffer_len - DHCP_FIXED_HEADER_SIZE;

        if (options_start[0] != 99 || options_start[1] != 130 ||
            options_start[2] != 83 || options_start[3] != 99) {
            std::cerr << "Magic cookie mismatch in get_dhcp_option_value! Got: "
                      << (int)options_start[0] << "." << (int)options_start[1]
                      << "." << (int)options_start[2] << "."
                      << (int)options_start[3] << std::endl;
            return false;
        }

        int current_offset = 4;

        while (current_offset < options_total_len) {
            uint8_t current_code = options_start[current_offset++];

            if (current_code == OPTION_PAD) {
                continue;
            }
            if (current_code == OPTION_END) {
                break;
            }

            if (current_offset >= options_total_len) {
                std::cerr << "Option length byte missing for code "
                          << (int)current_code << std::endl;
                return false;
            }
            uint8_t current_len = options_start[current_offset++];

            if (current_offset + current_len > options_total_len) {
                std::cerr << "Option data (len=" << (int)current_len
                          << ") exceeds buffer length for code "
                          << (int)current_code << std::endl;
                return false;
            }

            if (current_code == option_code_to_find) {
                uint8_t copy_len = std::min(current_len, max_value_len);
                if (value_out && copy_len > 0) {
                    memcpy(value_out, &options_start[current_offset], copy_len);
                }
                return true;
            }

            current_offset += current_len;
        }

        return false;
    }

    uint8_t get_dhcp_option_value_byte(const uint8_t* buffer,
                                       ssize_t buffer_len,
                                       uint8_t option_code_to_find) {
        uint8_t value = 0;
        if (get_dhcp_option_value(buffer, buffer_len, option_code_to_find,
                                  &value, 1)) {
            return value;
        }
        return 0;
    }

    std::string mac_to_string(const uint8_t* mac, uint8_t len) {
        if (len != 6) {
            if (len == 0) return "Invalid MAC (len=0)";
            len = 6;
        }
        char mac_str[18];
        snprintf(mac_str, sizeof(mac_str), "%02x:%02x:%02x:%02x:%02x:%02x",
                 mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
        return std::string(mac_str);
    }

    in_addr get_server_ip() {
        struct ifaddrs *ifaddr, *ifa;
        in_addr server_ip;
        server_ip.s_addr = inet_addr("0.0.0.0");
        static in_addr cached_server_ip = {0};

        if (cached_server_ip.s_addr != 0) {
            return cached_server_ip;
        }

        if (getifaddrs(&ifaddr) == -1) {
            perror("getifaddrs");
            return server_ip;
        }

        for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
            if (ifa->ifa_addr == NULL) continue;

            if (ifa->ifa_addr->sa_family == AF_INET &&
                !(ifa->ifa_flags & IFF_LOOPBACK) && (ifa->ifa_flags & IFF_UP) &&
                (ifa->ifa_flags & IFF_RUNNING)) {
                struct sockaddr_in* addr_in =
                    (struct sockaddr_in*)ifa->ifa_addr;

                if (strcmp(ifa->ifa_name, "eth0") == 0) {
                    server_ip = addr_in->sin_addr;
                    std::cout << "  Using server IP " << inet_ntoa(server_ip)
                              << " from interface " << ifa->ifa_name
                              << std::endl;
                    break;
                }

                if (server_ip.s_addr == inet_addr("0.0.0.0")) {
                    server_ip = addr_in->sin_addr;
                    std::cout << "  Tentatively using server IP "
                              << inet_ntoa(server_ip) << " from interface "
                              << ifa->ifa_name << " (will prefer eth0 if found)"
                              << std::endl;
                }
            }
        }

        freeifaddrs(ifaddr);

        if (server_ip.s_addr == inet_addr("0.0.0.0")) {
            std::cerr << "Warning: Could not determine a suitable server IP "
                         "address. Using 0.0.0.0."
                      << std::endl;
        } else {
            cached_server_ip = server_ip;
        }

        return server_ip;
    }

    void load_leases() {
        std::ifstream file("dhcp_leases.txt");
        if (!file.is_open()) {
            std::cout << "No existing lease file found or cannot open."
                      << std::endl;
            return;
        }
        std::string line;
        while (std::getline(file, line)) {
            std::istringstream iss(line);
            std::string mac_str, ip_str;
            time_t expiry;
            int declined_int;

            if (!(iss >> mac_str >> ip_str >> expiry >> declined_int)) {
                std::cerr << "Error parsing lease file line: " << line
                          << std::endl;
                continue;
            }

            Lease lease;

            if (inet_pton(AF_INET, ip_str.c_str(), &lease.ip_address) != 1) {
                std::cerr << "Invalid IP address format in lease file: "
                          << ip_str << std::endl;
                continue;
            }
            lease.expiry_time = expiry;
            lease.declined = (declined_int != 0);

            leases_[mac_str] = lease;
        }
        file.close();
        std::cout << "Loaded " << leases_.size()
                  << " leases from dhcp_leases.txt" << std::endl;
    }

    void save_leases() {
        std::ofstream file("dhcp_leases.txt");
        if (!file.is_open()) {
            std::cerr << "Error opening lease file for writing." << std::endl;
            return;
        }
        for (const auto& pair : leases_) {
            file << pair.first << " " << inet_ntoa(pair.second.ip_address)
                 << " " << pair.second.expiry_time << " "
                 << (pair.second.declined ? 1 : 0) << std::endl;
        }
        file.close();
        std::cout << "Saved leases to dhcp_leases.txt" << std::endl;
    }
};

int main() {
    try {
        DHCPServer server("172.20.0.100", "172.20.0.200", "255.255.0.0",
                          "172.20.0.1", "8.8.8.8", 3600);

        signal(SIGINT, signalHandler);
        signal(SIGTERM, signalHandler);

        std::thread server_thread(&DHCPServer::run, &server);

        while (keepRunning) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

        std::cout << "Shutting down initiated..." << std::endl;
        server.stop();
        server_thread.join();
        std::cout << "Server thread joined." << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return 1;
    }

    std::cout << "Exiting main." << std::endl;
    return 0;
}