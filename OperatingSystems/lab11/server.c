#include "fifo.h"

#define MAX_STUDENTS 100
#define MAX_NAME_LENGTH 100
#define NUM_SUBJECTS 3

struct Student {
    char name[MAX_NAME_LENGTH];
    int grades[NUM_SUBJECTS];
};


void process_file(const char *input_filename, const char *output_filename) {
    FILE *infile = fopen(input_filename, "rb");
    FILE *outfile = fopen(output_filename, "w");

    if (infile == NULL || outfile == NULL) {
        perror("Ошибка открытия файла");
        exit(1);
    }

    struct Student student;
    while (fread(&student, sizeof(struct Student), 1, infile) == 1) {
        int failed_exams = 0;
        for (int i = 0; i < NUM_SUBJECTS; i++) {
            if (student.grades[i] < 3) {
                failed_exams++;
            }
        }
        if (failed_exams > 0) {
            fprintf(outfile, "ФИО: %s, Несданные экзамены: %d\n", student.name, failed_exams);
        }
    }

    if (fclose(infile) != 0 || fclose(outfile) != 0) {
        perror("Ошибка закрытия файла");
        exit(1);
    }
}


int main() {
    int fifo_fd, client_fd;
    char buf[MAX_BUF];
    char filename[MAX_BUF];
    char output_filename[MAX_BUF];

    if (mknod(FIFO_NAME, S_IFIFO | 0666, 0) == -1) {
        if (errno != EEXIST) { 
            perror("Ошибка создания FIFO");
            exit(1);
        }
    }

    fifo_fd = open(FIFO_NAME, O_RDONLY);
    if (fifo_fd == -1) {
        perror("Ошибка открытия FIFO");
        exit(1);
    }

    while (1) {
        read(fifo_fd, buf, MAX_BUF);
        if (strncmp(buf, "FILENAME~", 9) == 0) {
            strcpy(filename, buf + 9);
            filename[strcspn(filename, "\n")] = 0;
            break;
        }
    }

    sprintf(output_filename, "output_%s", filename);
    process_file(filename, output_filename);

    client_fd = open(FIFO_NAME, O_WRONLY);
    if (client_fd < 0) {
        perror("Ошибка открытия FIFO для записи");
        exit(1);
    }

    write(client_fd, output_filename, strlen(output_filename) + 1);
    close(client_fd);
    close(fifo_fd);
    unlink(FIFO_NAME);

    return 0;
}