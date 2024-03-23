#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void swap(char *a, char *b) {
    char temp = *a;
    *a = *b;
    *b = temp;
}

void reverse(char str[], int len) {
    int i = 0, j = len - 1;
    while (i < j) {
        swap(&str[i], &str[j]);
        i++;
        j--;
    }
}

int findCeil(char str[], char first, int l, int h) {
    int ceilIndex = l;
    for (int i = l + 1; i <= h; i++) {
        if (str[i] > first && str[i] < str[ceilIndex]) {
            ceilIndex = i;
        }
    }
    return ceilIndex;
}

int factorial(int n) {
    if (n == 1 || n == 0) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

void sortedPermutations(char str[]) {
    int size = strlen(str);
    qsort(str, size, sizeof(char), (int (*)(const void *, const void *))strcmp);
    bool isFinished = false;
    while (!isFinished) {
        printf("%s\n", str);
        int i;
        for (i = size - 2; i >= 0; --i) {
            if (str[i] < str[i + 1]) {
                break;
            }
        }
        if (i == -1) {
            isFinished = true;
            break;
        }
        int ceilIndex = findCeil(str, str[i], i + 1, size - 1);
        swap(&str[i], &str[ceilIndex]);
        reverse(str + i + 1, size - i - 1);
    }
}

int main() {
    char str[100];
    printf("Введите множество элементов: ");
    scanf("%s", str);

    sortedPermutations(str);

    printf("Количество возможных перестановок: %d\n", factorial(strlen(str)));

    return 0;
}
