#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Функция для переворота строки
void reverse(char *str) {
    int len = strlen(str);
    int i = 0;        // Индекс начала строки
    int j = len - 1;  // Индекс конца строки
    char temp;

    while (i < j) {
        temp = str[i];
        str[i] = str[j];
        str[j] = temp;
        i++;
        j--;
    }
}

// Функция для удаления символа новой строки из строки
void remove_newline(char *str) {
    int len = strlen(str);
    if (len > 0 && str[len - 1] == '\n') {
        str[len - 1] = '\0';
    }
}

int main() {
    FILE *input;
    FILE *output;
    char line[100];

    input = fopen("input.txt", "r");
    if (input == NULL) {
        printf("Не удалось открыть входной файл.\n");
        exit(1);
    }

    output = fopen("output.txt", "w");
    if (output == NULL) {
        printf("Не удалось открыть выходной файл.\n");
        exit(2);
    }

    while (fgets(line, sizeof(line), input) != NULL) {
        remove_newline(line);
        reverse(line);
        fputs(line, output);
        fputc('\n', output);
    }

    fclose(input);
    fclose(output);

    return (0);
}