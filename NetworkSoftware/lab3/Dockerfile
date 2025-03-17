FROM ubuntu:latest

RUN apt-get update && apt-get install -y build-essential g++

WORKDIR /app
COPY . .

RUN g++ -o dhcp_server dhcp_server.cpp -pthread

CMD ["./dhcp_server"]