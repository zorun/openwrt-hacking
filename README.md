# OpenWrt hacking

This is a repository with some work-in-progress work for OpenWrt.

It currently contains dumps of mtd partitions from various router models,
along with ath10k calibration data.

## Tools

### Mikrotik Routerboot parsing

Mikrotik formats its configuration as TLV data, often directly written to MTD partitions
(`hard_config` or `soft_config`).

`tools/parse-routerboot.py` allows to parse this data structure.  It decodes
the basic structure, but some bits are still missing, for instance the
"Extended Radio Data" (ERD) part is often not correctly interpreted.

Here is an example that shows several configuration data (MAC address, router model...)

    $ tools/parse-routerboot.py hap-ac2/mtd3_hard_config.bin
    RB_MAGIC_HARD
    DATA type=26   len=4     data-offset=0x0008  00 00 00 00                          |....|
    DATA type=4    len=8     data-offset=0x0010  74 4d 28 5f d8 75 00 00              |tM(_.u..|
    DATA type=14   len=4     data-offset=0x001c  07 00 00 00                          |....|
    DATA type=10   len=4     data-offset=0x0024  e7 43 50 0a                          |.CP.|
    DATA type=13   len=4     data-offset=0x002c  00 00 00 08                          |....|
    DATA type=19   len=4     data-offset=0x0034  00 00 00 00                          |....|
    DATA type=18   len=4     data-offset=0x003c  00 00 02 00                          |....|
    DATA type=20   len=4     data-offset=0x0044  f4 dc 2e 0d                          |....|
    DATA type=21   len=4     data-offset=0x004c  00 40 28 08                          |.@(.|
    DATA type=27   len=4     data-offset=0x0054  88 13 00 00                          |....|
    DATA type=11   len=16    data-offset=0x005c  42 34 41 30 30 41 35 30 34 33 45 37  |B4A00A5043E7+
    DATA type=5    len=24    data-offset=0x0070  52 42 44 35 32 47 2d 35 48 61 63 44  |RBD52G-5HacD+
    DATA type=33   len=12    data-offset=0x008c  68 41 50 20 61 63 c2 b2 00 00 00 00  |hAP ac......|
    DATA type=6    len=12    data-offset=0x009c  36 2e 34 33 2e 31 30 00 00 00 00 00  |6.43.10.....|
    DATA type=25   len=20    data-offset=0x00ac  ff ff ff ff ff ff ff ff ff ff ff ff  |............+
    DATA type=3    len=20    data-offset=0x00c4  ef 70 18 00 0c 00 00 00 00 10 00 00  |.p..........+
    DATA type=23   len=8     data-offset=0x00dc  68 61 70 2d 64 6b 00 00              |hap-dk..|
    DATA type=37   len=4     data-offset=0x00e8  0a 66 2b 06                          |.f+.|
    DATA type=28   len=72    data-offset=0x00f0  a0 02 00 00 02 03 70 02 ac 02 00 00  |......p.....+
    DATA type=35   len=8     data-offset=0x013c  cc 02 00 00 00 00 00 00              |........|
    DATA type=22   len=2964  data-offset=0x0148  4c 5a 4f 52 00 0f 44 52 45 00 01 00  |LZOR..DRE...+
    Trying to recursively decode ERD partition
    RB_MAGIC_LZOR
    DATA type=3840 len=21060 data-offset=0x0008  45 00 01 00 3d 2f fc 20 2f 6f 5f 02  |E...=/. /o_.+
    Done decoding ERD
    Zero-length record with type 0, ending now

Another example:

    $ tools/parse-routerboot.py hap-lite/mtd4_soft_config.bin
    Unknown magic: 0x536f6674
    Trying again in big-endian mode
    RB_MAGIC_SOFT
    CRC: 0x1d10490d
    DATA type=12  len=4  data-offset=0x000c  00 00 00 10                |....|
    DATA type=17  len=4  data-offset=0x0014  00 00 00 00                |....|
    DATA type=10  len=4  data-offset=0x001c  00 00 00 02                |....|
    DATA type=1   len=4  data-offset=0x0024  00 00 00 00                |....|
    DATA type=2   len=4  data-offset=0x002c  00 00 00 02                |....|
    DATA type=3   len=4  data-offset=0x0034  00 00 00 01                |....|
    DATA type=4   len=4  data-offset=0x003c  00 00 00 00                |....|
    DATA type=5   len=4  data-offset=0x0044  00 00 00 00                |....|
    DATA type=7   len=4  data-offset=0x004c  00 00 00 00                |....|
    DATA type=9   len=4  data-offset=0x0054  00 00 00 00                |....|
    DATA type=15  len=4  data-offset=0x005c  00 00 00 00                |....|
    DATA type=21  len=4  data-offset=0x0064  00 00 00 00                |....|
    DATA type=23  len=4  data-offset=0x006c  00 00 00 00                |....|
    DATA type=27  len=4  data-offset=0x0074  00 00 00 00                |....|
    DATA type=31  len=4  data-offset=0x007c  00 14 02 58                |...X|
    DATA type=13  len=4  data-offset=0x0084  00 00 00 00                |....|
    DATA type=6   len=8  data-offset=0x008c  33 2e 34 31 00 00 00 00    |3.41....|
    DATA type=11  len=8  data-offset=0x0098  00 00 00 00 00 00 06 23    |.......#|
    Zero-length record with type 0, ending now

### LZO decompressor

It is common to use LZO compression in embedded devices, because it's very simple and fast to decode.
However, the `lzop` tool is not usable in that case, because it expects metadata in front of the compressed data.

`tools/minilzo` contains a very simple raw LZO decompressor as `decompressor.c`.  To build it, just run `make gcc`.

It will try to decompress as much input data as possible and output what it could decode, which is useful when analysing
unknown data.  You can optionally specify a number of bytes to skip in the input:

    $ tools/minilzo/decompressor 1466 < hap-ac-lite/mtd1_hard_config.bin | hexdump -C
    Skipping 1466 bytes of input.
    Read 2630 bytes from stdin.
    LZO return code is -6. Writing 301 bytes to stdout.
    00000000  ff ff ff 20 00 00 00 00  00 00 00 00 00 00 00 00  |... ............|
    00000010  00 00 00 e9 00 00 06 02  02 11 22 33 11 11 11 00  |.........."3....|
    00000020  33 00 00 01 1f 00 33 02  60 03 07 04 00 2c 00 4d  |3.....3.`....,.M|
    00000030  04 03 00 08 ff 80 05 07  10 01 10 00 22 22 02 00  |............""..|
    00000040  50 01 64 00 60 04 07 00  00 14 00 64 7d a4 af 00  |P.d.`......d}...|
    00000050  ff b4 01 27 14 00 0e 0e  0e 03 00 2c e2 00 02 0e  |...'.......,....|
    00000060  1c 80 c0 80 0c 80 c0 80  27 64 00 2e 20 00 0a 70  |........'d.. ..p|
    00000070  89 a2 fd 00 af 90 d4 80  fe 00 ad 8c 74 00 05 ab  |............t...|
    00000080  8c d4 80 fc 00 ab 90 76  00 a9 94 77 00 a8 94 d4  |.......v...w....|
    00000090  31 fc 00 01 70 ac 70 89  c9 00 26 c0 00 01 22 22  |1...p.p...&...""|
    000000a0  20 1e 2a 0c 00 07 1c 1a  20 1e 1c 1a 20 20 1c 14  | .*..... ...  ..|
    000000b0  74 02 36 35 00 20 71 04  18 41 05 18 64 05 3a 34  |t.65. q..A..d.:4|
    000000c0  00 00 02 11 12 15 17 41  42 45 47 31 32 35 37 70  |.......ABEG1257p|
    000000d0  75 9d a2 70 75 a2 ff 6c  00 05 7a 7f 93 98 70 75  |u..pu..l..z...pu|
    000000e0  ac b8 4d 00 00 6c 00 01  7a 7f 93 a2 7c 00 93 a2  |..M..l..z...|...|
    000000f0  7c 00 93 a2 7c 00 00 01  7a 7f 3c 7c 3c 3c 3c 7c  ||...|...z.<|<<<||
    00000100  3c 3c 7c 3c 3c 7c 7c 3c  3c 3c 3c 7c 3c 3c 3c 7c  |<<|<<||<<<<|<<<||
    00000110  3c 3c 3c 7c 7c 3c 3c 7c  3c 3c 3c 7c 3c 3c 3c 7c  |<<<||<<|<<<|<<<||
    00000120  3c 3c 3c 7c 7c 7c 3c 7c  7c 7c 10 01 00           |<<<|||<|||...|
    0000012d

To try to decode data, you can just run a bash loop that iterates on the possible offsets,
something like:

    $ for offset in {1450..1500}; do echo $offset; tools/minilzo/decompressor $offset < hap-ac-lite/mtd1_hard_config.bin | hexdump -C; done | less

The decompressor exits with the return code from the LZO routine, allowing to check
if decompression was successful.

TODO: check that the kernel LZO implementation (`lib/lzo/lzo1x_decompress_safe.c`)
actually produces the same output...

### Run-Length Encoding

Some router vendors sometimes use a very simple RLE encoding: <https://en.wikipedia.org/wiki/Run-length_encoding>

`tools/rle-decoder.py` implements a variant used by Mikrotik, inspired by this implementation <https://git.openwrt.org/?p=openwrt/openwrt.git;a=blob;f=target/linux/ar71xx/files/arch/mips/ath79/routerboot.c>

It also accepts a number of bytes to skip at the start of the input, to ease exploration.

    $ tools/rle-decoder.py 46 < hap-ac2/mtd3_hard_config_ext_wlan_data.bin
    Skipping 46 bytes from input
    00000000  10 00 00 10 33 00 00 00  08 00 08 00 00 00 00 00  |....3...........|
    00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000020  29 29 33 01 00 00 00 00  00 33 33 33 f4 f2 f2 00  |))3......333....|
    00000030  3c 14 06 00 f8 e3 8f 3f  ec 00 00 11 03 14 39 00  |<......?......9.|
    00000040  ff c0 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000050  00 00 90 01 00 00 00 00  01 00 ff ff ff ff 00 00  |................|
    00000060  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000070  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000080  00 00 00 00 00 00 00 00  0f 00 00 00 00 00 00 00  |................|
    00000090  00 00 10 00 10 00 10 00  10 00 00 00 00 00 00 00  |................|
    000000a0  00 00 68 05 00 05 00 00  00 00 00 00 00 00 00 00  |..h.............|
    000000b0  00 00 00 00 00 00 00 00  3f 14 00 00 00 00 00 00  |........?.......|
    000000c0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 b6 ff  |................|
    000000d0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    000000e0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    000000f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000100  0a 01 00 00 00 00 c3 cc  0c 00 20 a4 00 03 11 00  |.......... .....|
    00000110  fe 12 12 12 12 12 12 12  12 12 12 12 12 12 12 12  |................|
    00000120  12 12 12 12 12 a4 a4 a4  a4 a4 a4 a4 a4 a4 a4 a4  |................|
    00000130  a4 06 06 06 06 bd ff 00  1b 00 00 00 00 00 00 00  |................|
    00000140  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000150  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    00000160  00 10 12 12 12 12 12 12  12 12 12 12 12 12 12 12  |................|
    00000170  12 12 12 12 12 12 12 12  12 12 12 12 12 12 12 12  |................|
    00000180  12 12 12 12 12 12 12 12  12 12 12 12 12 12 12 12  |................|
    00000190  12 12 12 12 12 12 12 12  12 12 12 12 12 12 12 12  |................|
    000001a0  12 12 12 12 12 12 0c 0c  0c 0c 0c 0c 0c 0c 0c 0c  |................|
    000001b0  0c 0c 0c 0c 0c 0c 0c 0c  0c 0c 0c 0c 0c 0c 0c 0c  |................|
    000001c0  0c 0c 0c 0c 0c 0c 0c 0c  0c 0c 0c 0c 0c 0c 0c 0c  |................|

