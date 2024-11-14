#include "myheader.h"

char *optarg;
int opterr = 0;


void print_environment_1() {
    int i;
    for (i = 0; i < 10 && environ[i] != NULL; i++) {
        printf("environ[%d]: %s\n", i, environ[i]);
    }
}

void print_environment_2() {
    int i = 0;
    while (i < 10 && environ[i] != NULL) {
        puts(environ[i++]); 
    }
}

void print_file_content(const char *filename) {
    if (!filename) {
        fprintf(stderr, "Имя файла не указано.\n");
        return;
    }

    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Ошибка открытия файла");
        return;
    }

    int c;
    while ((c = fgetc(file)) != EOF) {
        putchar(c);
    }

    if (ferror(file)) {
        perror("Ошибка чтения файла");
    }

    if (fclose(file) != 0) {
        perror("Ошибка закрытия файла");
    }
}


void print_author_info(const char *fio, const char *user_id) {
    printf("\nАвтор: %s, ID: %s\n", fio, user_id);
}


int main(int argc, char *argv[]) {
    int option;
    int method = 0;
    char *filename = NULL;

    struct option long_options[] = {
        {"method1", no_argument, 0, '1'},
        {"method2", no_argument, 0, '2'},
        {"file", required_argument, 0, 'f'},
        {0, 0, 0, 0}
    };


    while ((option = getopt_long(argc, argv, "12f:", long_options, NULL)) != -1) {
        switch (option) {
            case '1':
                if (method != 0) {
                    fprintf(stderr, "Указаны несовместимые опции.\n");
                    return 1;
                }
                method = 1;
                break;
            case '2':
                if (method != 0) {
                    fprintf(stderr, "Указаны несовместимые опции.\n");
                    return 1;
                }
                method = 2;
                break;
            case 'f':
                filename = optarg;
                break;
            case '?':
                fprintf(stderr, "Неверная опция.\n");
                return 1;
            default:
                fprintf(stderr, "Ошибка обработки опций.\n");
                return 1;
        }
    }

    if (method == 1) {
        print_environment_1();
    } else if (method == 2) {
        print_environment_2();
    }

    print_file_content(filename);

    print_author_info("\tПономаренко Владимир", "ИА-231");

    return 0;
}