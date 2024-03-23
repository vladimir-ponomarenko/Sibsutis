#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#define HASHTAB_SIZE 200001

struct listnode {
    char *key;
    int value;
    struct listnode *next;
    int collisions;
};
struct listnode *hashtab[HASHTAB_SIZE];

void hashtab_init(struct listnode **hashtab);
unsigned int hashtab_hash(char *key, int hash_type);
void hashtab_add(struct listnode **hashtab, char *key, int value,
                 int hash_type);
struct listnode *hashtab_lookup(struct listnode **hashtab, char *key,
                                int hash_type);
void hashtab_delete(struct listnode **hashtab, char *key, int hash_type);