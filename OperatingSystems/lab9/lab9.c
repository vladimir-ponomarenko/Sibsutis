#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define MAX_STUDENTS 100
#define MAX_NAME_LENGTH 100
#define NUM_SUBJECTS 3

struct Student {
    char name[MAX_NAME_LENGTH];
    int grades[NUM_SUBJECTS];
};

void create_student_file(const char* filename) {
    FILE* file = fopen(filename, "wb");
    if (file == NULL) {
        perror("Ошибка открытия файла для записи");
        exit(EXIT_FAILURE);
    }

    struct Student students[] = {
        {"Иванов Иван Иванович", {5, 4, 3}},
        {"Петров Петр Петрович", {2, 3, 4}},
        {"Сидоров Сидор Сидорович", {5, 5, 5}},
        {"Козлова Анна Петровна", {4, 2, 5}},
        {"Смирнова Мария Ивановна", {3, 3, 2}}
    };
    int num_students = sizeof(students) / sizeof(students[0]);

    size_t written = fwrite(students, sizeof(struct Student), num_students, file);
    if (written != num_students) {
        perror("Ошибка записи в файл");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    if (fclose(file) != 0) {
        perror("Ошибка закрытия файла");
        exit(EXIT_FAILURE);
    }
}


void process_student_file(const char* filename) {
    FILE* file = fopen(filename, "rb");
    if (file == NULL) {
        perror("Ошибка открытия файла для чтения");
        exit(EXIT_FAILURE);
    }

    struct Student student;
    while (fread(&student, sizeof(struct Student), 1, file) == 1) {
        int failed_exams = 0;
        for (int i = 0; i < NUM_SUBJECTS; i++) {
            if (student.grades[i] < 3) {
                failed_exams++;
            }
        }
        if (failed_exams > 0) {
            printf("ФИО: %s, Несданные экзамены: %d\n", student.name, failed_exams);
        }
    }

    if (fclose(file) != 0) {
        perror("Ошибка закрытия файла");
        exit(EXIT_FAILURE);
    }
}


int main() {
    const char* filename = "STUDENT.dat";

    create_student_file(filename);
    process_student_file(filename);

    printf("Автор:\tПономаренко Владимир, ИА-231\n"); 

    return 0;
}