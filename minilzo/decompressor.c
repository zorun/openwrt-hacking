/* 
   Copyright (C) 2019 Baptiste Jonglez
   All Rights Reserved.

   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation; either version 2 of
   the License, or (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with the source code; see the file COPYING.
   If not, write to the Free Software Foundation, Inc.,
   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include "minilzo.h"

#define MAX_INPUT_LEN   16384
#define MAX_OUTPUT_LEN  65536


int main(int argc, char *argv[])
{
    unsigned char inbuf[MAX_INPUT_LEN];
    unsigned char outbuf[MAX_OUTPUT_LEN];
    size_t inlen = 0;
    size_t read_bytes;
    size_t outlen = MAX_OUTPUT_LEN;
    int skip_bytes = 0;
    int ret;

    /* Skip the given number of bytes from input. */
    if (argc > 1) {
        skip_bytes = atoi(argv[1]);
        fprintf(stderr, "Skipping %d bytes of input.\n", skip_bytes);
        while (skip_bytes > 0 && (read_bytes = read(STDIN_FILENO, inbuf, skip_bytes < MAX_INPUT_LEN ? skip_bytes : MAX_INPUT_LEN)) != 0) {
            skip_bytes -= read_bytes;
        }
    }

    /* Read the rest */
    while (inlen < MAX_INPUT_LEN && (read_bytes = read(STDIN_FILENO, inbuf + inlen, MAX_INPUT_LEN - inlen)) != 0) {
        inlen += read_bytes;
    }
    fprintf(stderr, "Read %lu bytes from stdin.\n", inlen);

    /* Decompress and output */
    ret = lzo1x_decompress_safe(inbuf, inlen, outbuf, &outlen, NULL);
    fprintf(stderr, "LZO return code is %d. Writing %lu bytes to stdout.\n", ret, outlen);
    write(STDOUT_FILENO, outbuf, outlen);
}
