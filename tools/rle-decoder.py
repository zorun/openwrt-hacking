#!/usr/bin/env python3

import binascii
import ctypes
import sys

import hexdump


def signed_char(char):
    return ctypes.c_int8(char).value

def rle_decode(buf):
    out = b""
    size = len(buf)
    pos = 0
    while pos < size:
        count = signed_char(buf[pos])
        pos += 1
        if count == 0:
            break
        # Next char is repeated [count] times
        if count > 0:
            out += buf[pos:pos+1] * count
            pos += 1
        # The next [- count] chars are just copied as-is
        if count < 0:
            count = -1 * count
            out += buf[pos:pos+count]
            pos += count
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1:
        skip = int(sys.argv[1])
        print("Skipping {} bytes from input".format(skip), file=sys.stderr)
        sys.stdin.buffer.read(skip)
    out = rle_decode(sys.stdin.buffer.read())
    hexdump.hexdump(out)
