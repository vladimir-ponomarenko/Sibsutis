#include "fifo.h"

void print_file_content(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Ошибка открытия файла");
        exit(1);
    }

    int c;
    while ((c = fgetc(file)) != EOF) {
        putchar(c);
    }

    if (fclose(file) != 0) {
        perror("Ошибка закрытия файла");
        exit(1);
    }
}


int main() {
    int fifo_fd;
    char buf[MAX_BUF];
    char filename[MAX_BUF];
    char server_message[MAX_BUF];


    fifo_fd = open(FIFO_NAME, O_WRONLY);
    if (fifo_fd == -1) {
        perror("Ошибка открытия FIFO");
        exit(1);
    }

    printf("Введите имя файла: ");
    fgets(filename, MAX_BUF, stdin);
    filename[strcspn(filename, "\n")] = 0; 

    sprintf(buf, "FILENAME~%s\n", filename);
    write(fifo_fd, buf, strlen(buf));
    close(fifo_fd);


    fifo_fd = open(FIFO_NAME, O_RDONLY);
    if (fifo_fd < 0) {
        perror("Ошибка открытия FIFO для чтения");
        exit(1);
    }

    read(fifo_fd, server_message, MAX_BUF);
    close(fifo_fd);

    print_file_content(server_message);

    return 0;
}
