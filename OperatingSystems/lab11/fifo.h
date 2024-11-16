#ifndef FIFO_H
#define FIFO_H

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>

#ifndef S_IFIFO
#define S_IFIFO 0010000
#endif


#define FIFO_NAME "myfifo" 
#define MAX_BUF 256

#endif