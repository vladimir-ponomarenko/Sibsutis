#include <stdio.h>
#include <stdlib.h>
#define M 5

void rand_matrix(int A[][M], int m, int n) {
    int i, j;
    for (i = 0; i < m; i++) {
        for (j = 0; j < n; j++) {
            A[i][j] = rand() % 50 - 25;
            printf("%d ", A[i][j]);
        }
        printf("\n");
    }
}

void print_matrix(int A[][M], int m, int n) {
    int i, j;
    for (i = 0; i < m; i++) {
        for (j = 0; j < n; j++) {
            printf("Введите элемент %d %d \n", i, j);
            scanf("%d", &A[i][j]);
        }
        printf("\n");
    }
    for (i = 0; i < m; i++) {
        for (j = 0; j < n; j++) {
            printf("%d ", A[i][j]);
        }
        printf("\n");
    }
}

void otr(int A[][M], int m, int n) {
    int i, j;
    int k = 0;
    int mx = 0;
    int imx = 0;
    for (i = 0; i < m; i++) {
        k = 0;
        for (j = 0; j < n; j++) {
            if (A[i][j] < 0) {
                k++;
            }
        }
        if (k > mx) {
            mx = k;
            imx = i;
        }
    }
    printf("Строка номер: %d \n", imx);
}

void sum(int A[][M], int m, int n) {
    int i, j, k;
    int sum = 0;
    k = n;
    for (i = 0; i < m; i++) {
        k = k - 1;
        int pob = A[i][k];
        sum = 0;
        for (j = 0; j < n; j++) {
            sum = sum + A[i][j];
        }
        printf("Сумма строки %d равна: %d \n", i, sum);
        if (sum < 15) {
            for (j = 0; j < n; j++) {
                A[i][j] = A[i][j] + pob;
            }
        }
    }
    for (i = 0; i < m; i++) {
        for (j = 0; j < n; j++) {
            printf("%d ", A[i][j]);
        }
        printf("\n");
    }
}

int main() {
    int n1, m1;
    int Matr1[M][M];
    int choice;
    printf(" 1 - рандомное заполнение; 2 - ввод пользователем. \n ");
    scanf("%d", &choice);
    if (choice == 1) {
        printf("Введите размерность матрицы: \n");
        scanf("%d%d", &m1, &n1);
        rand_matrix(Matr1, m1, n1);
    }
    if (choice == 2) {
        printf("Введите размерность матрицы: \n");
        scanf("%d%d", &m1, &n1);
        print_matrix(Matr1, m1, n1);
    }
    otr(Matr1, m1, n1);
    sum(Matr1, m1, n1);
}