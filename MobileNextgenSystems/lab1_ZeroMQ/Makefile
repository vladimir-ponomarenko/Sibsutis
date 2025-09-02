CC = gcc
CFLAGS = -Wall -Wextra -Wpedantic -Werror -std=c11 -O2 -g -pthread -D_POSIX_C_SOURCE=200809L
LDFLAGS = -lzmq -luuid

SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin

COMMON_SRC = $(SRC_DIR)/common.c
COMMON_OBJ = $(OBJ_DIR)/common.o

SERVER_SRC = $(SRC_DIR)/server.c
SERVER_OBJ = $(OBJ_DIR)/server.o

CLIENT_SRC = $(SRC_DIR)/client.c
CLIENT_OBJ = $(OBJ_DIR)/client.o

SERVER_TARGET = $(BIN_DIR)/chat_server
CLIENT_TARGET = $(BIN_DIR)/chat_client

.PHONY: all clean run_server run_client

all: $(SERVER_TARGET) $(CLIENT_TARGET)

$(SERVER_TARGET): $(SERVER_OBJ) $(COMMON_OBJ)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(CLIENT_TARGET): $(CLIENT_OBJ) $(COMMON_OBJ)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	@rm -rf $(OBJ_DIR) $(BIN_DIR)

run_server: $(SERVER_TARGET)
	@./$(SERVER_TARGET)

run_client: $(CLIENT_TARGET)
	@./$(CLIENT_TARGET)