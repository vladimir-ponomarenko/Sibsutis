#include <stdio.h>
#define MAX_SIZE 100

int main() {
    int n, i, j, is_reflexive = 1, is_symmetric = 1, is_antisymmetric = 1,
                 is_transitive = 1;
    int matrix[MAX_SIZE][MAX_SIZE];
    printf("Введите размер множества: ");
    scanf("%d", &n);
    printf("Введите элементы множества:\n");
    for (i = 0; i < n; i++) {
        int element;
        scanf("%d", &element);
    }
    printf("Введите количество упорядоченных пар: ");
    int num_pairs;
    scanf("%d", &num_pairs);
    printf("Введите упорядоченные пары:\n");
    for (i = 0; i < num_pairs; i++) {
        int a, b;
        scanf("%d %d", &a, &b);
        matrix[a - 1][b - 1] = 1;
    }
stop:
    // Проверка на рефлексивность
    for (i = 0; i < n; i++) {
        if (matrix[i][i] != 1) {
            is_reflexive = 0;
            break;
        }
    }
    // Проверка на симметричность
    for (i = 0; i < n; i++) {
        for (j = 0; j < i; j++) {
            if (matrix[i][j] != matrix[j][i]) {
                is_symmetric = 0;
                break;
            }
        }
    }
    // Проверка на антисимметричность
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            if (matrix[i][j] == 1 && matrix[j][i] == 1 && i != j) {
                is_antisymmetric = 0;
                break;
            }
        }
    }
    // Проверка на транзитивность
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            if (matrix[i][j] == 1) {
                int k;
                for (k = 0; k < n; k++) {
                    if (matrix[j][k] == 1 && matrix[i][k] != 1) {
                        is_transitive = 0;
                        break;
                    }
                }
            }
        }
    }
    // Вывод результатов
    printf("Матрица бинарного отношения:\n");
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            printf("%d ", matrix[i][j]);
        }
        printf("\n");
    }
    printf("Свойства данного отношения:\n");
    if (is_reflexive) {
        printf("Рефлексивное\n");
    } else {
        printf("Не рефлексивное\n");
    }
    if (is_symmetric) {
        printf("Симметричное\n");
    } else {
        printf("Не симметричное\n");
    }
    if (is_antisymmetric) {
        printf("Антисимметричное\n");
    } else {
        printf("Не антисимметричное\n");
    }
    if (is_transitive) {
        printf("Транзитивное\n");
    } else {
        printf("Не транзитивное\n");
    }
    // Возможность изменения заданного бинарного отношения
    while (1) {
        printf("Хотите изменить заданный бинарный отношение? (y/n): ");
        char choice;
        scanf(" %c", &choice);
        if (choice == 'y' || choice == 'Y') {
            printf(
                "Введите номер строки и столбца, которые вы хотите изменить: ");
            int row, col;
            scanf("%d %d", &row, &col);
            printf("Введите новое значение (0 или 1): ");
            int value;
            scanf("%d", &value);
            matrix[row - 1][col - 1] = value;
            printf("Матрица бинарного отношения после изменения:\n");
            printf(" ");
            for (i = 0; i < n; i++) {
                printf("%d ", i + 1);
            }
            printf("\n");
            for (i = 0; i < n; i++) {
                printf("%d ", i + 1);
                for (j = 0; j < n; j++) {
                    printf("%d ", matrix[i][j]);
                }
                printf("\n");
            }
        } else {
            goto stop;
        }
    }
}
