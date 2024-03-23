#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_NAME_LEN 50
#define MAX_PHONE_LEN 20
#define MAX_ABONENTS 100

struct Abonent {
    char name[MAX_NAME_LEN];
    char phone[MAX_PHONE_LEN];
};

void add_abonent(struct Abonent *abonents, int *num_abonents) {
    if (*num_abonents == MAX_ABONENTS) {
        printf("Error: maximum number of abonents reached\n");
        return;
    }
    printf("Enter the name of the abonent: ");
    scanf("%s", abonents[*num_abonents].name);
    printf("Enter the phone number of the abonent: ");
    scanf("%s", abonents[*num_abonents].phone);
    FILE *file = fopen("abonent.dat", "ab");
    if (file == NULL) {
        printf("Ошибка открытия файла \n");
        return;
    }
    fwrite(&abonents[*num_abonents], sizeof(struct Abonent), 1, file);
    fclose(file);
    *num_abonents += 1;
}

void process_abonents(struct Abonent *abonents, int num_abonents) {
    char name_to_find[MAX_NAME_LEN];
    printf("Enter the name of the abonent: ");
    scanf("%s", name_to_find);
    FILE *file = fopen("abonent.dat", "rb");
    if (file == NULL) {
        printf("Ошибка открытия файла \n");
        return;
    }
    struct Abonent abonent;
    int found = 0;
    for (int i = 0; i < num_abonents; i++) {
        (fread(&abonents[num_abonents], sizeof(struct Abonent), 1, file));
        if (strcmp(abonents[i].name, name_to_find) == 0) {
            printf("Phone number: %s\n", abonents[i].phone);
            found = 1;
            // break;
        }

        /*  if (strcmp(abonents[i].name, name_to_find) == 0) {
              printf("Phone number: %s\n", abonents[i].phone);
              found = 1;
              break;
          }*/
    }
    if (!found) {
        printf("Abonent not found\n");
    }
    fclose(file);
}

int main() {
    struct Abonent abonents[MAX_ABONENTS];
    int num_abonents = 0;
    int exit = 0;
    while (!exit) {
        printf("Select operation:\n");
        printf("a) Add or start a new file\n");
        printf("b) Process existing file\n");
        char operation;
        scanf(" %c", &operation);
        switch (operation) {
            case 'a':
                // num_abonents = 0;
                add_abonent(abonents, &num_abonents);
                break;
            case 'b':
                process_abonents(abonents, num_abonents);
                break;
            default:
                printf("Invalid operation\n");
                break;
        }
        printf("Do you want to continue? (y/n): ");
        char answer;
        scanf(" %c", &answer);
        exit = (answer == 'n');
    }
    return 0;
}
