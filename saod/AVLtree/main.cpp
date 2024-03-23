#include <iostream>
#include <fstream>
#include <string>
#include <cstring>
#include <time.h>
#include <iomanip>

struct avltree {
    int key;
    char* value;
    struct avltree* left;
    struct avltree* right;
    int height;
    bool deleted;
};

int max(int a, int b) {
    return (a > b) ? a : b;
}

int height(struct avltree* node) {
    if (node == nullptr)
        return 0;
    return node->height;
}

int get_balance(struct avltree* node) {
    if (node == nullptr)
        return 0;
    return height(node->left) - height(node->right);
}

struct avltree* new_node(int key, char* value) {
    struct avltree* node = new struct avltree;
    node->key = key;
    node->value = strdup(value);
    node->left = nullptr;
    node->right = nullptr;
    node->height = 1;
    node->deleted = false;
    return node;
}

struct avltree* right_rotate(struct avltree* y) {
    struct avltree* x = y->left;
    struct avltree* T2 = x->right;

    x->right = y;
    y->left = T2;

    y->height = max(height(y->left), height(y->right)) + 1;
    x->height = max(height(x->left), height(x->right)) + 1;

    return x;
}

struct avltree* left_rotate(struct avltree* x) {
    struct avltree* y = x->right;
    struct avltree* T2 = y->left;

    y->left = x;
    x->right = T2;

    x->height = max(height(x->left), height(x->right)) + 1;
    y->height = max(height(y->left), height(y->right)) + 1;

    return y;
}

struct avltree* avltree_add(struct avltree* root, int key, char* value) {
    if (root == nullptr)
        return new_node(key, value);

    if (key < root->key)
        root->left = avltree_add(root->left, key, value);
    else if (key > root->key)
        root->right = avltree_add(root->right, key, value);
    else {
        if (root->deleted) {
            free(root->value);
            root->value = strdup(value);
            root->deleted = false;
        }
        return root;
    }

    root->height = 1 + max(height(root->left), height(root->right));

    int balance = get_balance(root);

    // Left-Left Case
    if (balance > 1 && key < root->left->key)
        return right_rotate(root);

    // Right-Right Case
    if (balance < -1 && key > root->right->key)
        return left_rotate(root);

    // Left-Right Case
    if (balance > 1 && key > root->left->key) {
        root->left = left_rotate(root->left);
        return right_rotate(root);
    }

    // Right-Left Case
    if (balance < -1 && key < root->right->key) {
        root->right = right_rotate(root->right);
        return left_rotate(root);
    }

    return root;
}

struct avltree* avltree_lookup(struct avltree* root, int key) {
    if (root == nullptr)
        return nullptr;

    if (key == root->key && !root->deleted)
        return root;

    if (key < root->key)
        return avltree_lookup(root->left, key);

    return avltree_lookup(root->right, key);
}

struct avltree* avltree_delete(struct avltree* root, int key) {
    if (root == nullptr)
        return root;

    if (key < root->key)
        root->left = avltree_delete(root->left, key);
    else if (key > root->key)
        root->right = avltree_delete(root->right, key);
    else {
        if (!root->deleted) {
            root->deleted = true;
            free(root->value);
            root->value = nullptr;
        }
    }

    if (root == nullptr)
        return root;

    root->height = 1 + max(height(root->left), height(root->right));

    int balance = get_balance(root);

    // Left-Left Case
    if (balance > 1 && get_balance(root->left) >= 0)
        return right_rotate(root);

    // Left-Right Case
    if (balance > 1 && get_balance(root->left) < 0) {
        root->left = left_rotate(root->left);
        return right_rotate(root);
    }

    // Right-Right Case
    if (balance < -1 && get_balance(root->right) <= 0)
        return left_rotate(root);

    // Right-Left Case
    if (balance < -1 && get_balance(root->right) > 0) {
        root->right = right_rotate(root);
        return left_rotate(root);
    }

    return root;
}


struct avltree* avltree_min(struct avltree* root) {
    struct avltree* current = root;
    while (current->left != nullptr)
        current = current->left;
    return current;
}

struct avltree* avltree_max(struct avltree* root) {
    struct avltree* current = root;
    while (current->right != nullptr)
        current = current->right;
    return current;
}

void avltree_free(struct avltree* root) {
    if (root == nullptr)
        return;

    avltree_free(root->left);
    avltree_free(root->right);

    free(root->value);
    delete root;
}

void avltree_print_dfs(struct avltree* root, int level) {
    if (root == nullptr)
        return;

    avltree_print_dfs(root->right, level + 1);

    for (int i = 0; i < level; i++)
        std::cout << "  ";

    if (!root->deleted)
        std::cout << root->key << " (" << root->value << ")" << std::endl;
    else
        std::cout << root->key << " (Deleted)" << std::endl;

    avltree_print_dfs(root->left, level + 1);
}


int main() {
    struct avltree* root = nullptr;
    std::ifstream wordsFile("words.txt");
    std::string word;
    int insertedWords = 0;

     // Вставка элементов в дерево из файла
    while (insertedWords < 50000 && std::getline(wordsFile, word)) {
        root = avltree_add(root, insertedWords, strdup(word.c_str()));
        insertedWords++;
    }

    for (int num_nodes = 2500; num_nodes <= 50000; num_nodes +=2500 ) {
       
        // Замер времени выполнения поиска случайного ключа
        clock_t start_time = clock();
              for (int j = 0; j < 1000000; j++) {

        struct avltree* found = avltree_lookup(root, rand() % num_nodes + 1);
              }
        clock_t end_time = clock();

        double time_elapsed = ((double)(end_time - start_time)) / CLOCKS_PER_SEC;
           std::cout << "Nodes: " << num_nodes << ", Time: " << std::fixed << std::setprecision(50) << time_elapsed/1000000 << " seconds" << std::endl;
    }

    std::cout << "Inserted " << insertedWords << " words into the AVL tree." << std::endl;

    while (true) {
        std::cout << "Choose an action:" << std::endl;
        std::cout << "1. Search for a word by key" << std::endl;
        std::cout << "2. Delete a word by key" << std::endl;
        std::cout << "3. Print the tree" << std::endl;
        std::cout << "4. Exit" << std::endl;

        int choice;
        std::cout << "Enter your choice (1-4): ";
        std::cin >> choice;

        switch (choice) {
            case 1: {
                int key;
                std::cout << "Enter the key to search: ";
                std::cin >> key;
                struct avltree* found = avltree_lookup(root, key);
                if (found && !found->deleted)
                    std::cout << "Found: " << found->value << std::endl;
                else
                    std::cout << "Not found." << std::endl;
                break;
            }

            case 2: {
                int key;
                std::cout << "Enter the key to delete: ";
                std::cin >> key;
                root = avltree_delete(root, key);
                break;
            }

            case 3:
                avltree_print_dfs(root, 0);
                break;

            case 4:
                // Освобождение памяти перед завершением
                avltree_free(root);
                return 0;

            default:
                std::cout << "Invalid choice. Please enter a valid option (1-4)." << std::endl;
                break;
        }
    }

    return 0;
}
