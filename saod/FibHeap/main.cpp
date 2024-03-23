#include <climits>
#include <cmath>
#include <iostream>

struct FibHeapNode {
    int key;
    char* value;
    int degree;
    bool mark;
    FibHeapNode* parent;
    FibHeapNode* child;
    FibHeapNode* left;
    FibHeapNode* right;

    FibHeapNode(int k, char* val)
        : key(k),
          value(val),
          degree(0),
          mark(false),
          parent(nullptr),
          child(nullptr),
          left(this),
          right(this) {}
};

struct FibHeap {
    FibHeapNode* min;
    int nnodes;

    FibHeap() : min(nullptr), nnodes(0) {}

    FibHeapNode* fibheap_insert(int key, char* value) {
        FibHeapNode* node = new FibHeapNode(key, value);
        if (min == nullptr) {
            min = node;
        } else {
            FibHeapNode* oldMin = min;
            node->left = oldMin;
            node->right = oldMin->right;
            oldMin->right = node;
            node->right->left = node;
            if (key < min->key) {
                min = node;
            }
        }
        nnodes++;
        return node;
    }

    FibHeapNode* fibheap_min() { return min; }

    void fibheap_link(FibHeapNode* y, FibHeapNode* x) {
        y->left->right = y->right;
        y->right->left = y->left;
        y->parent = x;
        if (x->child == nullptr) {
            x->child = y;
            y->left = y;
            y->right = y;
        } else {
            FibHeapNode* firstChild = x->child;
            FibHeapNode* lastChild = firstChild->left;
            firstChild->left = y;
            lastChild->right = y;
            y->left = lastChild;
            y->right = firstChild;
        }
        x->degree++;
        y->mark = false;
    }

    void fibheap_consolidate() {
        int maxDegree = static_cast<int>(log2(nnodes)) + 1;
        FibHeapNode* A[maxDegree];
        for (int i = 0; i < maxDegree; i++) {
            A[i] = nullptr;
        }

        FibHeapNode* x = min;
        int numRoots = 0;
        if (x != nullptr) {
            numRoots++;
            x = x->right;
            while (x != min) {
                numRoots++;
                x = x->right;
            }
        }

        while (numRoots > 0) {
            int d = x->degree;
            FibHeapNode* next = x->right;
            while (A[d] != nullptr) {
                FibHeapNode* y = A[d];
                if (x->key > y->key) {
                    FibHeapNode* temp = x;
                    x = y;
                    y = temp;
                }
                fibheap_link(y, x);
                A[d] = nullptr;
                d++;
            }
            A[d] = x;
            x = next;
            numRoots--;
        }

        min = nullptr;
        for (int i = 0; i < maxDegree; i++) {
            if (A[i] != nullptr) {
                if (min == nullptr || A[i]->key < min->key) {
                    min = A[i];
                }
            }
        }
    }

    FibHeapNode* fibheap_delete_min() {
        FibHeapNode* z = min;
        if (z != nullptr) {
            FibHeapNode* child = z->child;
            for (int i = 0; i < z->degree; i++) {
                FibHeapNode* nextChild = child->right;
                child->left = z;
                child->right = z->right;
                z->right->left = child;
                z->right = child;
                child->parent = nullptr;
                child = nextChild;
            }
            z->left->right = z->right;
            z->right->left = z->left;
            if (z == z->right) {
                min = nullptr;
            } else {
                min = z->right;
                fibheap_consolidate();
            }
            nnodes--;
        }
        return z;
    }

    void fibheap_decrease_key(FibHeapNode* x, int newkey) {
        if (newkey > x->key) {
            return;
        }
        x->key = newkey;
        FibHeapNode* y = x->parent;
        if (y != nullptr && x->key < y->key) {
            fibheap_cut(x, y);
            fibheap_cascading_cut(y);
        }
        if (x->key < min->key) {
            min = x;
        }
    }

    void fibheap_cut(FibHeapNode* x, FibHeapNode* y) {
        if (x == x->right) {
            y->child = nullptr;
        } else {
            if (y->child == x) {
                y->child = x->right;
            }
            x->left->right = x->right;
            x->right->left = x->left;
        }
        y->degree--;
        x->left = min;
        x->right = min->right;
        min->right->left = x;
        min->right = x;
        x->parent = nullptr;
        x->mark = false;
    }

    void fibheap_cascading_cut(FibHeapNode* y) {
        FibHeapNode* z = y->parent;
        if (z != nullptr) {
            if (!y->mark) {
                y->mark = true;
            } else {
                fibheap_cut(y, z);
                fibheap_cascading_cut(z);
            }
        }
    }

    void fibheap_delete(FibHeapNode* x) {
        fibheap_decrease_key(x, INT_MIN);
        fibheap_delete_min();
    }
};

FibHeapNode* findNodeByKey(FibHeap& heap, int key) {
    if (heap.min == nullptr) return nullptr;

    FibHeapNode* startNode = heap.min;
    FibHeapNode* currentNode = startNode;

    do {
        if (currentNode->key == key) {
            return currentNode;
        }
        currentNode = currentNode->right;
    } while (currentNode != startNode);

    return nullptr;
}

int main() {
    FibHeap heap;

    while (true) {
        int choice;
        std::cout << "Fibonacci Heap Menu:" << std::endl;
        std::cout << "1. Insert a node" << std::endl;
        std::cout << "2. Find the minimum node" << std::endl;
        std::cout << "3. Decrease key" << std::endl;
        std::cout << "4. Delete minimum node" << std::endl;
        std::cout << "5. Exit" << std::endl;
        std::cout << "Enter your choice (1-5): ";
        std::cin >> choice;

        if (choice == 1) {
            int key;
            char value[100];
            std::cout << "Enter the key: ";
            std::cin >> key;
            std::cout << "Enter the value: ";
            std::cin >> value;
            heap.fibheap_insert(key, value);
            std::cout << "Node inserted." << std::endl;
        } else if (choice == 2) {
            FibHeapNode* minNode = heap.fibheap_min();
            if (minNode != nullptr) {
                std::cout << "Minimum node: Key = " << minNode->key
                          << ", Value = " << minNode->value << std::endl;
            } else {
                std::cout << "The heap is empty." << std::endl;
            }
        } else if (choice == 3) {
            int key, newKey;
            std::cout << "Enter the key to decrease: ";
            std::cin >> key;
            std::cout << "Enter the new key: ";
            std::cin >> newKey;

            FibHeapNode* nodeToDecrease = findNodeByKey(heap, key);

            if (nodeToDecrease != nullptr) {
                heap.fibheap_decrease_key(nodeToDecrease, newKey);
                std::cout << "Key decreased successfully." << std::endl;
            } else {
                std::cout << "Node with key " << key
                          << " not found in the heap." << std::endl;
            }
        } else if (choice == 4) {
            FibHeapNode* minNode = heap.fibheap_delete_min();
            if (minNode != nullptr) {
                std::cout << "Deleted node: Key = " << minNode->key
                          << ", Value = " << minNode->value << std::endl;
            } else {
                std::cout << "The heap is empty." << std::endl;
            }
        } else if (choice == 5) {
            break;
        } else {
            std::cout << "Invalid choice. Please enter a valid option."
                      << std::endl;
        }
    }

    return 0;
}
