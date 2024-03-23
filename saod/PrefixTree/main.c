#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ALPHABET_SIZE \
    33  // Для символов 'A' - 'Z', '$' и дополнительного символа '\0'

// Структура для узла префиксного дерева (trie)
struct trie {
    char ch;
    char* value;
    struct trie* sibling;
    struct trie* child;
};

// Функция для создания пустого узла
struct trie* trie_create() {
    struct trie* node = (struct trie*)malloc(sizeof(struct trie));
    if (node) {
        node->ch = '\0';
        node->value = NULL;
        node->sibling = NULL;
        node->child = NULL;
    }
    return node;
}

// Функция для получения дочернего узла, соответствующего символу c
struct trie* GetChild(struct trie* node, char c) {
    struct trie* child = node->child;
    while (child && child->ch != c) {
        child = child->sibling;
    }
    return child;
}

// Функция для установки дочернего узла, соответствующего символу c
void SetChild(struct trie* node, char c, struct trie* child) {
    child->ch = c;
    child->sibling = node->child;
    node->child = child;
}

// Функция для вставки ключа и значения в префиксное дерево
struct trie* TrieInsert(struct trie* root, const char* key, char* value) {
    struct trie* node = root;
    for (int i = 0; key[i] != '\0'; i++) {
        struct trie* child = GetChild(node, key[i]);
        if (!child) {
            child = trie_create();
            SetChild(node, key[i], child);
        }
        node = child;
    }
    if (node->value) {
        free(node->value);  // Освобождаем старое значение, если оно существует
    }
    node->value = strdup(value);
    return root;
}

// Функция для поиска значения по ключу
struct trie* TrieLookup(struct trie* root, const char* key) {
    struct trie* node = root;
    for (int i = 0; key[i] != '\0'; i++) {
        struct trie* child = GetChild(node, key[i]);
        if (!child) {
            return NULL;  // Ключ не найден
        }
        node = child;
    }
    if (node->value == NULL) {
        return NULL;  // Ключ найден, но это не завершающий узел
    }
    return node;
}

// Функция для удаления значения по ключу
struct trie* TrieDelete(struct trie* root, const char* key) {
    struct trie* node = root;
    struct trie* parent = NULL;
    struct trie* to_delete = NULL;
    for (int i = 0; key[i] != '\0'; i++) {
        parent = node;
        struct trie* child = GetChild(node, key[i]);
        if (!child) {
            return root;  // Ключ не найден, ничего не удаляем
        }
        if (to_delete) {
            // Освобождаем дочерние узлы, так как мы двигаемся наверх в дереве
            free(to_delete->value);
            free(to_delete);
            to_delete = NULL;
        }
        if (parent && parent->child == child) {
            parent->child = child->sibling;
        } else {
            parent->sibling = child->sibling;
        }
        to_delete = child;
        node = child;
    }
    if (node) {
        if (node->value) {
            free(node->value);  // Освобождаем значение
            node->value = NULL;
        }
        if (to_delete) {
            free(to_delete);  // Освобождаем узел
        }
    }
    return root;
}

// Функция для освобождения памяти, выделенной для префиксного дерева
void TrieFree(struct trie* root) {
    if (root) {
        TrieFree(root->child);
        TrieFree(root->sibling);
        if (root->value) {
            free(root->value);
        }
        free(root);
    }
}

// Функция для печати префиксного дерева (для отладки)
void TriePrint(struct trie* root, int level) {
    if (root) {
        for (int i = 0; i < level; i++) {
            printf("  ");
        }
        printf("%c (%s)\n", root->ch, root->value);
        TriePrint(root->child, level + 1);
        TriePrint(root->sibling, level);
    }
}

int main() {
    struct trie* root = trie_create();
    struct trie* found;  // Переменную found объявляем здесь

    int choice;
    char key[100];  // Допустим, максимальная длина ключа - 100 символов
    char value[100];  // Максимальная длина значения - 100 символов

    while (1) {
        printf("Выберите действие:\n");
        printf("1. Вставить слово\n");
        printf("2. Найти слово\n");
        printf("3. Удалить слово\n");
        printf("4. Вывести дерево\n");
        printf("5. Выйти\n");

        printf("Введите номер действия: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                printf("Введите слово : ");
                scanf("%s", key);
                printf("Введите значение: ");
                scanf("%s", value);
                root = TrieInsert(root, key, value);
                printf("Слово добавлено в дерево.\n");
                break;
            case 2:
                printf("Введите слово для поиска: ");
                scanf("%s", key);
                found = TrieLookup(root, key);
                if (found) {
                    printf("Найдено: %s\n", found->value);
                } else {
                    printf("Слово не найдено.\n");
                }
                break;
            case 3:
                printf("Введите слово для удаления: ");
                scanf("%s", key);
                root = TrieDelete(root, key);
                printf("Слово удалено из дерева.\n");
                break;
            case 4:
                TriePrint(root, 0);
                break;
            case 5:
                TrieFree(root);
                exit(0);
                break;
            default:
                printf("Некорректный выбор. Пожалуйста, выберите снова.\n");
                break;
        }
    }

    return 0;
}
