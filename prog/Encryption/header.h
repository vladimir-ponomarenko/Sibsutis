#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define ROWS 5
#define COLUMNS 6
#define ROWS_RU 6
#define COLUMNS_RU 6

int contains(char * s, char c);

void create_table(char * key, char table[ROWS][COLUMNS]);
void playfair_encrypt(char table[ROWS][COLUMNS], char * plaintext, char *ciphertext);
void playfair_decrypt(char table[ROWS][COLUMNS], char * ciphertext, char *plaintext);
void create_table_RU(char* key, char table[ROWS_RU][COLUMNS_RU]);
void playfair_encrypt_RU(char table[ROWS_RU][COLUMNS_RU], char* plaintext, char*ciphertext);
void playfair_decrypt_RU(char table[ROWS_RU][COLUMNS_RU], char* ciphertext, char*plaintext);