#include "bstree.h"
#include "hashtab.h"

int main() {
    int choice;
    printf(
        "Choose: 1 or 2 or 3 \n 1) 1 and 2 experiment. \n 2) 6 "
        "Experiment(KR).\n 3) 6 Experiment(ELF)\n");
    scanf("%d", &choice);
    switch (choice) {
        case 1:;

            double cpu_time_usedadd1;
            double cpu_time_usedadd2;

            // struct timeval start, end;
            char word[200000];
            FILE* fp;
            fp = fopen("words.txt", "r");
            if (fp == NULL) {
                printf("Error opening file\n");
                return -1;
            }
            struct bstree *tree, *node1;
            tree = bstree_create(200001, "Koala");

            struct listnode* node;
            hashtab_init(hashtab);
            for (int n = 10000; n <= 200000; n += 10000) {
                // rewind(fp);
                fseek(fp, n, SEEK_SET);
                clock_t startadd1 = clock();
                clock_t startadd2 = clock();
                for (int i = 0; i < n; i++) {
                    if (fgets(word, 100000, fp) == NULL) {
                        printf("End of file reached\n");
                        return -1;
                    }
                    // Удаление символов новой строки из слова
                    word[strcspn(word, "\n")] = '\0';
                    bstree_add(tree, i, word);
                    hashtab_add(hashtab, word, i, 1);
                    if (i == n - 1) {
                        clock_t endadd1 = clock();
                        cpu_time_usedadd1 =
                            ((double)(endadd1 - startadd1)) / CLOCKS_PER_SEC;
                        printf(
                            "Time used for bstree_add with %d words: %.12f "
                            "seconds\n",
                            n, cpu_time_usedadd1 / n);

                        clock_t endadd2 = clock();
                        cpu_time_usedadd2 =
                            ((double)(endadd2 - startadd2)) / CLOCKS_PER_SEC;
                        printf(
                            "Time used for hashtab_add with %d words: %.12f "
                            "seconds\n \n",
                            n, cpu_time_usedadd2 / n);
                    }
                }

                // binary tree time:
                clock_t start = clock();
                // gettimeofday(&start, NULL);
                for (int j = 0; j < 10000; j++) {
                    /* if (fgets(word, 100000, fp) == NULL) {
                         printf("End of file reached\n");
                         return -1;
                     }*/
                    node1 = bstree_lookup(tree, 9999);
                }
                // gettimeofday(&end, NULL);
                // double elapsed_time =(end.tv_sec - start.tv_sec)+(end.tv_usec
                // - start.tv_usec)/1000000.0;
                clock_t end = clock();
                double cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;

                // hashtab time:
                clock_t starttab = clock();
                for (int j = 0; j < 100000; j++) {
                    node = hashtab_lookup(hashtab, "ambilaevous", 1);
                }
                clock_t endtab = clock();
                double cpu_time_usedtab =
                    ((double)(endtab - starttab)) / CLOCKS_PER_SEC;

                printf(
                    "Time used for bstree_lookup with %d words: %.12f "
                    "seconds\nTime used for hashtab_lookup with %d words: "
                    "%.12f seconds\n",
                    n, cpu_time_used / 10000, n, cpu_time_usedtab / 100000);
                printf(
                    "----------------------------------------------------------"
                    "------------");
                printf("\n");
            }
            fclose(fp);
            exit(1);
        case 2:;
            int collisions = 0;
            char word2[200000];
            FILE* fp2;
            fp2 = fopen("words.txt", "r");
            if (fp2 == NULL) {
                printf("Error opening file\n");
                return -1;
            }
            // struct listnode * node;
            hashtab_init(hashtab);
            double cpu_time_usedadd3;

            for (int n = 10000; n <= 200000; n += 10000) {
                fseek(fp2, n, SEEK_SET);
                for (int i = 0; i < n; i++) {
                    if (fgets(word2, 100000, fp2) == NULL) {
                        printf("End of file reached\n");
                        return -2;
                    }
                    word2[strcspn(word2, "\n")] = '\0';
                    hashtab_add(hashtab, word2, i, 2);
                }
                clock_t startadd3 = clock();
                for (int j = 0; j <= 100000; j++) {
                    node = hashtab_lookup(hashtab, "ambilaevous", 2);
                }
                clock_t endadd3 = clock();
                double cpu_time_usedadd3 =
                    ((double)(endadd3 - startadd3)) / CLOCKS_PER_SEC;

                for (int j = 1; j <= HASHTAB_SIZE; j += 1) {
                    struct listnode* curr = hashtab[j];
                    while (curr != NULL) {
                        collisions += curr->collisions;
                        curr->collisions = 0;
                        curr = curr->next;
                    }
                }

                printf(
                    "Time used for hashtab_lookup(KR) with %d words: %.30f "
                    "seconds, collisions: %d\n \n",
                    n, cpu_time_usedadd3 / 100000, collisions);
                collisions = 0;
            }
            fclose(fp2);

            exit(2);
        case (3):;
            collisions = 0;
            char word4[200000];
            FILE* fp4;
            fp4 = fopen("words.txt", "r");
            if (fp4 == NULL) {
                printf("Error opening file\n");
                return -1;
            }
            // struct listnode * node;
            hashtab_init(hashtab);
            double cpu_time_usedadd4;

            for (int n = 10000; n <= 200000; n += 10000) {
                fseek(fp4, n, SEEK_SET);
                for (int i = 0; i < n; i++) {
                    if (fgets(word4, 100000, fp4) == NULL) {
                        printf("End of file reached\n");
                        return -2;
                    }
                    word4[strcspn(word4, "\n")] = '\0';
                    hashtab_add(hashtab, word4, i, 3);
                }
                clock_t startadd4 = clock();
                for (int j = 0; j < 100000; j++) {
                    node = hashtab_lookup(hashtab, "ambilaevous", 3);
                }
                clock_t endadd4 = clock();
                double cpu_time_usedadd4 =
                    ((double)(endadd4 - startadd4)) / CLOCKS_PER_SEC;

                for (int j = 1; j <= HASHTAB_SIZE; j += 1) {
                    struct listnode* curr = hashtab[j];
                    while (curr != NULL) {
                        collisions += curr->collisions;
                        curr->collisions = 0;
                        curr = curr->next;
                    }
                }
                printf(
                    "Time used for hashtab_lookup(ELF) with %d words: %.30f "
                    "seconds, collisions: %d\n \n",
                    n, cpu_time_usedadd4 / 100000, collisions);
                collisions = 0;
            }
            fclose(fp4);
            exit(4);
        default:
            printf("Incorrect choice.\n");
            exit(5);
    }
}