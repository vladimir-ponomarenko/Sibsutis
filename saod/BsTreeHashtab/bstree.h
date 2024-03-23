#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

struct bstree {
    int key;     /* Ключ */
    char *value; /* Значение */

    struct bstree *left;
    struct bstree *right;
};

struct bstree *bstree_create(int key, char *value);
void bstree_add(struct bstree *tree, int key, char *value);
struct bstree *bstree_lookup(struct bstree *tree, int key);
struct bstree *bstree_min(struct bstree *tree);
struct bstree *bstree_max(struct bstree *tree);
struct bstree *bstree_delete(struct bstree *tree, int key);