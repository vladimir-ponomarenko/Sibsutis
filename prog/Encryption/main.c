#include "header.h"
#define BUFFER_SIZE 1024
int main(int argc, char* argv[]) {
    if (argc != 5) {
        fprintf(stderr, "Usage: %s EN|RU KEY INPUT_FILE OUTPUT_FILE\n",
                argv[0]);
        return 1;
    }
    int is_ru_mode = strcmp(argv[1], "RU") == 0;
    char* key = argv[2];
    char* input_file_name = argv[3];
    char* output_file_name = argv[4];
    FILE* input_file = fopen(input_file_name, "r");
    if (!input_file) {
        fprintf(stderr, "Failed to open input file %s\n", input_file_name);
        return 1;
    }
    char word_buffer[BUFFER_SIZE];
    if (!fgets(word_buffer, BUFFER_SIZE, input_file)) {
        fprintf(stderr, "Failed to read word from input file %s\n",
                input_file_name);
        return 1;
    }
    // Удаление символа переноса строки в конце слова, если он есть
    size_t word_len = strlen(word_buffer);
    if (word_len > 0 && word_buffer[word_len - 1] == '\n') {
        word_buffer[word_len - 1] = '\0';
    }
    char* word = strdup(word_buffer);
    fclose(input_file);
    int table_rows;
    int table_cols;
    if (is_ru_mode) {
        table_rows = ROWS_RU;
        table_cols = COLUMNS_RU;
    } else {
        table_rows = ROWS;
        table_cols = COLUMNS;
    }
    char ciphertext[BUFFER_SIZE];
    char decryptedtext[BUFFER_SIZE];
    char table[table_rows][table_cols];
    if (is_ru_mode) {
        create_table_RU(key, table);
        playfair_encrypt_RU(table, word, ciphertext);
        playfair_decrypt_RU(table, ciphertext, decryptedtext);
    } else {
        create_table(key, table);
        playfair_encrypt(table, word, ciphertext);
        playfair_decrypt(table, ciphertext, decryptedtext);
    }
    // Запись результатов в файл
    FILE* output_file = fopen(output_file_name, "w");
    if (!output_file) {
        fprintf(stderr, "Failed to open output file %s\n", output_file_name);
        return 1;
    }
    fprintf(output_file, "Table:\n");
    for (int i = 0; i < table_rows; i++) {
        for (int j = 0; j < table_cols; j++) {
            fprintf(output_file, "%c ", table[i][j]);
        }
        fprintf(output_file, "\n");
    }
    fprintf(output_file, "Plaintext: %s\n", word_buffer);
    fprintf(output_file, "Ciphertext: %s\n", ciphertext);
    fprintf(output_file, "Decrypted text: %s\n", decryptedtext);
    if (strcmp(word_buffer, word) == 0) {
        fprintf(output_file, "Decryption successful!\n");
    } else {
        fprintf(output_file, "Decryption failed.\n");
    }
    fclose(output_file);
    free(word);
    printf("Done. Results written to %s\n", output_file_name);
    return 22;
}