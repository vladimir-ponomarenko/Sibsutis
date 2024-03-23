#include "hashtab.h"

void hashtab_init(struct listnode** hashtab) {
    int i;

    for (i = 0; i < HASHTAB_SIZE; i++) hashtab[i] = NULL;
}

unsigned int hashtab_hash(char* key, int hash_type) {
    // hash_type 1-default;2-KR;3-ELF;
    unsigned int h = 0, hash_mul = 31, g;
    while (*key) {
        if (hash_type == 1) {
            h = h * hash_mul + (unsigned int)*key++;
        }
        if (hash_type == 2) {
            h = h * hash_mul + (unsigned int)*key++;
        }
        if (hash_type == 3) {
            h = (h << 4) + (unsigned int)*key++;
            g = h & 0xF0000000L;
            if (g) h ^= g >> 24;
            h &= ~g;
        }
    }
    return h % HASHTAB_SIZE;
}

void hashtab_add(struct listnode** hashtab, char* key, int value,
                 int hash_type) {
    struct listnode* node;

    int index = hashtab_hash(key, hash_type);
    node = malloc(sizeof(*node));
    if (node != NULL) {
        node->key = key;
        node->value = value;
        node->collisions = 0;
        node->next = NULL;

        if (hashtab[index] != NULL) {
            hashtab[index]->collisions++;
        }
        node->next = hashtab[index];
        hashtab[index] = node;
    }
}

struct listnode* hashtab_lookup(struct listnode** hashtab, char* key,
                                int hash_type) {
    struct listnode* node;

    int index = hashtab_hash(key, hash_type);
    for (node = hashtab[index]; node != NULL; node = node->next) {
        if (0 == strcmp(node->key, key)) return node;
    }
    return NULL;
}

void hashtab_delete(struct listnode** hashtab, char* key, int hash_type) {
    struct listnode *node, *prev = NULL;
    int index = hashtab_hash(key, hash_type);
    for (node = hashtab[index]; node != NULL; node = node->next) {
        if (0 == strcmp(node->key, key)) {
            if (prev == NULL)
                hashtab[index] = node->next;
            else
                prev->next = node->next;
            free(node);
            return;
        }
        prev = node;
    }
}