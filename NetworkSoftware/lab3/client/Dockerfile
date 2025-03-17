FROM ubuntu:latest

RUN apt-get update && apt-get install -y iputils-ping isc-dhcp-client net-tools

# Скрипт для запроса DHCP и вывода информации
COPY dhcp_request.sh /
RUN chmod +x /dhcp_request.sh

CMD ["/dhcp_request.sh"]