#include "header.h"
int contains(char* s, char c) {
    for (int i = 0; i < strlen(s); i++) {
        if (s[i] == c) {
            return 1;
        }
    }
    return 0;
}
void create_table(char* key, char table[ROWS][COLUMNS]) {
    int i, j, k;
    int len = strlen(key);
    for (i = 0; i < len; i++) {
        key[i] = tolower(key[i]);
    }
    // copy key to temp
    char temp[len];
    strcpy(temp, key);
    // remove duplicate letters
    for (i = 0; i < len; i++) {
        for (j = i + 1; j < len;) {
            if (temp[j] == temp[i]) {
                for (k = j; k < len; k++) {
                    temp[k] = temp[k + 1];
                }
                len--;
            } else {
                j++;
            }
        }
    }
    // add remaining letters to temp
    char alphabet[] = "abcdefghijklmnopqrstuvwxyz .,-";
    for (i = 0; i < strlen(alphabet); i++) {
        if (!contains(temp, alphabet[i])) {
            temp[len] = alphabet[i];
            len++;
        }
    }
    // populate table
    k = 0;
    for (i = 0; i < ROWS; i++) {
        for (j = 0; j < COLUMNS; j++) {
            table[i][j] = temp[k];
            k++;
        }
    }
}
void playfair_encrypt(char table[ROWS][COLUMNS], char* plaintext,
                      char* ciphertext) {
    int i, j, k;
    int len = strlen(plaintext);
    int x1, x2, y1, y2;
    char c1, c2;
    for (i = 0; i < len; i++) {
        plaintext[i] = tolower(plaintext[i]);
    }
    // replace j with i
    for (i = 0; i < len; i++) {
        if (plaintext[i] == 'J') {
            plaintext[i] = 'I';
        }
    }
    // add padding if necessary
    if (len % 2 != 0) {
        plaintext[len] = 'X';
        len++;
    }
    // encrypt plaintext
    k = 0;
    for (i = 0; i < len; i += 2) {
        c1 = plaintext[i];
        c2 = plaintext[i + 1];
        // find positions in table
        for (j = 0; j < ROWS; j++) {
            if (contains(table[j], c1)) {
                x1 = j;
                y1 = (int)(strchr(table[j], c1) - table[j]);
            }
            if (contains(table[j], c2)) {
                x2 = j;
                y2 = (int)(strchr(table[j], c2) - table[j]);
            }
        }
        if (y1 == y2) {  // same column
            ciphertext[k] = table[(x1 + 1) % ROWS][y1];
            ciphertext[k + 1] = table[(x2 + 1) % ROWS][y2];
        } else if (x1 == x2) {  // same row
            ciphertext[k] = table[x1][(y1 + 1) % COLUMNS];
            ciphertext[k + 1] = table[x2][(y2 + 1) % COLUMNS];
        } else {  // rectangle
            ciphertext[k] = table[x1][y2];
            ciphertext[k + 1] = table[x2][y1];
        }
        k += 2;
    }
    ciphertext[k] = '\0';  // terminate string
}
void playfair_decrypt(char table[ROWS][COLUMNS], char* ciphertext,
                      char* plaintext) {
    int i, j, k;
    int len = strlen(ciphertext);
    int x1, x2, y1, y2;
    char c1, c2;
    // decrypt ciphertext
    k = 0;
    for (i = 0; i < len; i += 2) {
        c1 = ciphertext[i];
        c2 = ciphertext[i + 1];
        // find positions in table
        for (j = 0; j < ROWS; j++) {
            if (contains(table[j], c1)) {
                x1 = j;
                y1 = (int)(strchr(table[j], c1) - table[j]);
            }
            if (contains(table[j], c2)) {
                x2 = j;
                y2 = (int)(strchr(table[j], c2) - table[j]);
            }
        }
        if (y1 == y2) {  // same column
            plaintext[k] = table[(x1 + ROWS - 1) % ROWS][y1];
            plaintext[k + 1] = table[(x2 + ROWS - 1) % ROWS][y2];
        } else if (x1 == x2) {  // same row
            plaintext[k] = table[x1][(y1 + COLUMNS - 1) % COLUMNS];
            plaintext[k + 1] = table[x2][(y2 + COLUMNS - 1) % COLUMNS];
        } else {  // rectangle
            plaintext[k] = table[x1][y2];
            plaintext[k + 1] = table[x2][y1];
        }
        k += 2;
    }
    plaintext[k] = '\0';  // terminate string
    // remove padding if necessary
    if (plaintext[k - 1] == 'X') {
        plaintext[k - 1] = '\0';
    }
    // replace i with j
    for (i = 0; i < k; i++) {
        if (plaintext[i] == 'I') {
            plaintext[i] = 'J';
        }
    }
}
void create_table_RU(char* key, char table[ROWS_RU][COLUMNS_RU]) {
    int i, j, k;
    int len = strlen(key);
    for (i = 0; i < len; i++) {
        key[i] = tolower(key[i]);
    }
    // copy key to temp
    char temp[100];
    strcpy(temp, key);
    // remove duplicate letters
    for (i = 0; i < len; i++) {
        for (j = i + 1; j < len;) {
            if (temp[j] == temp[i]) {
                for (k = j; k < len; k++) {
                    temp[k] = temp[k + 1];
                }
                len--;
            } else {
                j++;
            }
        }
    }
    // add remaining letters to temp
    char alphabet[] = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,-";
    for (i = 0; i < strlen(alphabet); i++) {
        if (!contains(temp, alphabet[i])) {
            temp[len] = alphabet[i];
            len++;
        }
    }
    // populate table
    k = 0;
    for (i = 0; i < ROWS_RU; i++) {
        for (j = 0; j < COLUMNS_RU; j++) {
            table[i][j] = temp[k];
            k++;
        }
    }
}
void playfair_encrypt_RU(char table[ROWS_RU][COLUMNS_RU], char* plaintext,
                         char* ciphertext) {
    int i, j, k;
    int len = strlen(plaintext);
    int x1, x2, y1, y2;
    char c1, c2;
    for (i = 0; i < len; i++) {
        plaintext[i] = tolower(plaintext[i]);
    }
    // add padding if necessary
    // encrypt plaintext
    k = 0;
    for (i = 0; i < len; i += 2) {
        c1 = plaintext[i];
        c2 = plaintext[i + 1];
        // find positions in table
        for (j = 0; j < ROWS_RU; j++) {
            if (contains(table[j], c1)) {
                x1 = j;
                y1 = (int)(strchr(table[j], c1) - table[j]);
            }
            if (contains(table[j], c2)) {
                x2 = j;
                y2 = (int)(strchr(table[j], c2) - table[j]);
            }
        }
        if (x1 == x2) {  // same row
            ciphertext[k] = table[x1][(y1 + 1) % COLUMNS_RU];
            ciphertext[k + 1] = table[x2][(y2 + 1) % COLUMNS_RU];
        } else if (y1 == y2) {  // same column
            ciphertext[k] = table[(x1 + 1) % ROWS_RU][y1];
            ciphertext[k + 1] = table[(x2 + 1) % ROWS_RU][y2];
        } else {  // rectangle
            ciphertext[k] = table[x1][y2];
            ciphertext[k + 1] = table[x2][y1];
        }
        k += 2;
    }
    ciphertext[k] = '\0';  // terminate string
}
void playfair_decrypt_RU(char table[ROWS_RU][COLUMNS_RU], char* ciphertext,
                         char* plaintext) {
    int i, j, k;
    int len = strlen(ciphertext);
    int x1, x2, y1, y2;
    char c1, c2;
    // decrypt ciphertext
    k = 0;
    for (i = 0; i < len; i += 2) {
        c1 = ciphertext[i];
        c2 = ciphertext[i + 1];
        // find positions in table
        for (j = 0; j < ROWS_RU; j++) {
            if (contains(table[j], c1)) {
                x1 = j;
                y1 = (int)(strchr(table[j], c1) - table[j]);
            }
            if (contains(table[j], c2)) {
                x2 = j;
                y2 = (int)(strchr(table[j], c2) - table[j]);
            }
        }
        if (x1 == x2) {  // same row
            plaintext[k] = table[x1][(y1 + COLUMNS_RU - 1) % COLUMNS_RU];
            plaintext[k + 1] = table[x2][(y2 + COLUMNS_RU - 1) % COLUMNS_RU];
        } else if (y1 == y2) {  // same column
            plaintext[k] = table[(x1 + ROWS_RU - 1) % ROWS_RU][y1];
            plaintext[k + 1] = table[(x2 + ROWS_RU - 1) % ROWS_RU][y2];
        } else {  // rectangle
            plaintext[k] = table[x1][y2];
            plaintext[k + 1] = table[x2][y1];
        }
        k += 2;
    }
    plaintext[k] = '\0';  // terminate string
}
