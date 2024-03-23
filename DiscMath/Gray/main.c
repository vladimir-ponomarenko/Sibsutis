#include <math.h>
#include <stdio.h>
#include <stdlib.h>

void gray_code(int n, int *set) {
    int i, j, k;
    int *gray = (int *)malloc(pow(2, n) * sizeof(int));
    for (i = 0; i < pow(2, n); i++) {
        gray[i] = i ^ (i >> 1);
    }
    for (i = 0; i < pow(2, n); i++) {
        printf("%d: ", i);
        for (j = n - 1; j >= 0; j--) {
            k = gray[i] >> j;
            if (k & 1) {
                printf("1");
            } else {
                printf("0");
            }
        }
        printf(" (");
        for (j = 0; j < n; j++) {
            if (gray[i] & (1 << j)) {
                printf("%d ", set[j]);
            }
        }
        printf(")\n");
    }
    free(gray);
}

int main() {
    int n, i, j;
    printf("Хотите задать исходное множество? (y/n): ");
    char choice;
    scanf(" %c", &choice);
    if (choice == 'y') {
        printf("Введите элементы множества, разделенные пробелами: ");
        scanf("%d", &n);
        int *set = (int *)malloc(n * sizeof(int));
        for (i = 0; i < n; i++) {
            scanf("%d", &set[i]);
        }
        gray_code(n, set);
        free(set);
    } else {
        printf("Введите мощность множества: ");
        scanf("%d", &n);
        int *set = (int *)malloc(n * sizeof(int));
        for (i = 0; i < n; i++) {
            set[i] = i + 1;
        }
        gray_code(n, set);
        free(set);
    }
    return 0;
}
