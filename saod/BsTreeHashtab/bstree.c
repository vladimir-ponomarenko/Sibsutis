#include "bstree.h"

struct bstree *bstree_create(int key, char *value) {
    struct bstree *node;

    node = malloc(sizeof(*node));
    if (node != NULL) {
        node->key = key;
        node->value = value;
        node->left = NULL;
        node->right = NULL;
    }
    return node;
}

void bstree_add(struct bstree *tree, int key, char *value) {
    if (tree == NULL) return;
    struct bstree *parent, *node;
    while (tree != NULL) {
        parent = tree;
        if (key < tree->key)
            tree = tree->left;
        else if (key > tree->key)
            tree = tree->right;
        else
            return;
    }
    node = bstree_create(key, value);
    if (key < parent->key)
        parent->left = node;
    else
        parent->right = node;
}

struct bstree *bstree_lookup(struct bstree *tree, int key) {
    while (tree != NULL) {
        if (key == tree->key)
            return tree;
        else if (key < tree->key)
            tree = tree->left;
        else
            tree = tree->right;
    }
    return tree;
}

struct bstree *bstree_min(struct bstree *tree) {
    if (tree == NULL) return NULL;

    while (tree->left != NULL) tree = tree->left;
    return tree;
}

struct bstree *bstree_max(struct bstree *tree) {
    if (tree == NULL) return NULL;

    while (tree->right != NULL) tree = tree->right;
    return tree;
}

struct bstree *bstree_delete(struct bstree *tree, int key) {
    if (tree == NULL) {
        // Если дерево пустое, возвращаем NULL
        return NULL;
    }

    if (key < tree->key) {
        // Если ключ меньше ключа текущего узла, рекурсивно вызываем функцию для
        // левого поддерева
        tree->left = bstree_delete(tree->left, key);
    } else if (key > tree->key) {
        // Если ключ больше ключа текущего узла, рекурсивно вызываем функцию для
        // правого поддерева
        tree->right = bstree_delete(tree->right, key);
    } else {
        // Если ключ совпадает с ключом текущего узла

        if (tree->left == NULL && tree->right == NULL) {
            // Если у узла нет детей (листовой узел), просто удаляем его
            free(tree);
            return NULL;
        } else if (tree->left == NULL) {
            // Если у узла есть только правый ребенок, заменяем узел на его
            // правого ребенка
            struct bstree *right_child = tree->right;
            free(tree);
            return right_child;
        } else if (tree->right == NULL) {
            // Если у узла есть только левый ребенок, заменяем узел на его
            // левого ребенка
            struct bstree *left_child = tree->left;
            free(tree);
            return left_child;
        } else {
            // Если у узла есть оба ребенка

            // Находим узел с наименьшим ключом в правом поддереве
            struct bstree *min_right = tree->right;
            while (min_right->left != NULL) {
                min_right = min_right->left;
            }

            // Копируем ключ и значение из найденного узла в текущий узел
            tree->key = min_right->key;
            tree->value = min_right->value;

            // Рекурсивно удаляем найденный узел с наименьшим ключом
            tree->right = bstree_delete(tree->right, min_right->key);
        }
    }

    return tree;
}