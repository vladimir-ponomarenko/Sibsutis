#include <stdio.h>
#include <stdlib.h>

struct node {
    int value;
    struct node *prev;
    struct node *next;
};

typedef struct node Node;

int main() {
    int n, value, value1;
    char choice;
    printf("Введите количество элементов списка: ");
    scanf("%d", &n);

    // Создание массива элементов списка
    Node *nodes = (Node *)malloc(n * sizeof(Node));
    for (int i = 0; i < n; i++) {
        printf("Введите значение элемента %d: ", i + 1);
        scanf("%d", &value);
        nodes[i].value = value;
        nodes[i].prev = NULL;
        nodes[i].next = NULL;
    }

    // Связывание элементов списка
    for (int i = 0; i < n; i++) {
        if (i > 0) {
            nodes[i].next = &nodes[i - 1];
        }
    }

    printf("Введите значение нижнего элемента: ");
    scanf("%d", &value1);

    Node *lowerElement = (Node *)malloc(sizeof(Node));
    lowerElement->value = value1;
    lowerElement->prev = NULL;
    lowerElement->next = &nodes[n - 1];

    nodes[0].prev = lowerElement;
    nodes[0].next = NULL;

    for (int i = 1; i < n - 1; i++) {
        nodes[i].prev = lowerElement;
    }

    Node *current = &nodes[0];

    while (1) {
        printf("Текущий элемент: %d\n", current->value);
        printf(
            "Введите символ для перемещения (n - следующий элемент, p - "
            "предыдущий элемент, q - выйти из программы): ");
        scanf(" %c", &choice);
        if (choice == 'n') {
            if (current->next != NULL) {
                current = current->next;
            } else {
                printf("Вы достигли конца списка.\n");
            }
        } else if (choice == 'p') {
            if (current->prev != NULL) {
                current = current->prev;
            } else {
                printf("Вы достигли начала списка.\n");
            }
        } else if (choice == 'q') {
            break;
        } else {
            printf("Неверный символ.\n");
        }
    }
    return 0;
}
