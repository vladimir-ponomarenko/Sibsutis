#ifndef MYHEADER_H
#define MYHEADER_H

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <getopt.h>

extern char **environ;
extern char *optarg;
extern int opterr;

void print_environment_1();
void print_environment_2();
void print_file_content(const char *filename);
void print_author_info(const char *fio, const char *user_id);

#endif