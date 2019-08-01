#!/usr/bin/env python3

"""
Decodes a Mikrotik "hard_config" or "soft_config" partition.

Inspired from arch/mips/ath79/routerboot.c and rbcfg
"""

import sys

import hexdump


RB_MAGIC_HARD = 0x64726148  # String for "Hard" in little-endian
RB_MAGIC_SOFT = 0x74666F53  # String for "Soft" in little-endian
RB_MAGIC_ERD  = 0x00455244  # "ERD"
RB_MAGIC_LZOR = 0x524f5a4c  # "LZOR"
RB_MAGICS = {RB_MAGIC_HARD: "RB_MAGIC_HARD",
             RB_MAGIC_SOFT: "RB_MAGIC_SOFT",
             RB_MAGIC_ERD:  "RB_MAGIC_ERD",
             RB_MAGIC_LZOR: "RB_MAGIC_LZOR"}


def uint16(buf, byteorder='little'):
    return int.from_bytes(buf[:2], byteorder=byteorder, signed=False)

def uint32(buf, byteorder='little'):
    return int.from_bytes(buf[:4], byteorder=byteorder, signed=False)

def decode_rb(buf, byteorder='little'):
    MAX_PRINT_LENGTH = 25
    pos = 0
    magic = uint32(buf[pos:], byteorder); pos += 4
    if magic not in RB_MAGICS.keys():
        print("Unknown magic: 0x{:08x}".format(magic), file=sys.stderr)
        if byteorder == 'little':
            print("Trying again in big-endian mode", file=sys.stderr)
            return decode_rb(buf, byteorder='big')
        return
    print(RB_MAGICS[magic])
    if magic == RB_MAGIC_SOFT:
        crc = uint32(buf[pos:], byteorder); pos += 4
        print("CRC: 0x{:08x}".format(crc))
    # TLV-formatted data follow
    while pos < len(buf):
        if byteorder == 'little':
            type_ = uint16(buf[pos:], byteorder); pos += 2
            length = uint16(buf[pos:], byteorder); pos += 2
        else:
            length = uint16(buf[pos:], byteorder); pos += 2
            type_ = uint16(buf[pos:], byteorder); pos += 2
        # routerboot.c has this "align" hack...  What the heck?
        if magic == RB_MAGIC_ERD:
            length = (length + 3) // 4
        if length == 0 and type_ == 0:
            print("Zero-length record with type 0, ending now")
            break
        header = "DATA type={:<5} len={:<5} data-offset=0x{:04x}".format(type_, length, pos)
        bin_data = buf[pos:pos+min(length, MAX_PRINT_LENGTH)]
        hex_data = hexdump.bin_to_hex(bin_data)
        ascii_data = hexdump.bin_to_ascii(bin_data)
        print("{:46} {:75} |{}{}".format(header, hex_data, ascii_data, "+" if length > MAX_PRINT_LENGTH else "|"))
        if type_ == 22:
            print("Trying to recursively decode ERD partition")
            decode_rb(buf[pos:pos+length], byteorder)
            print("Done decoding ERD")
        pos += length


if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], "rb") as f:
            data = f.read()
        decode_rb(data)
    else:
        decode_rb(sys.stdin.buffer.read())
