import string


# Bytestring of printable ASCII characters.
# We remove the \t, \n, \r and other strange whitespace characters
PRINTABLE_BYTES = string.printable.encode()[:-5]

def is_printable(byte):
    """Is the given byte printable as ASCII?"""
    return byte in PRINTABLE_BYTES

def bin_to_ascii(data):
    """Given bytes, return a best-effort ASCII representation (one char per byte)"""
    return "".join("%c" % byte if is_printable(byte) else '.' for byte in data)

def bin_to_hex(data):
    """Given bytes, return an hexadecimal representation (for n bytes, returns 3n-1 chars)"""
    return " ".join("%02x" % byte for byte in data)

def hexdump(data):
    """Produces an output similar to hexdump -C"""
    CHUNKSIZE = 16
    i = 0
    while i < len(data):
        dump1 = data[i:i+CHUNKSIZE//2]
        hex1 = " ".join("%02x" % byte for byte in dump1)
        dump2 = data[i+CHUNKSIZE//2:i+CHUNKSIZE]
        hex2 = " ".join("%02x" % byte for byte in dump2)
        text = bin_to_ascii(data[i:i+CHUNKSIZE])
        print("{:08x}  {:23}  {:23}  |{}|".format(i, hex1, hex2, text))
        i += CHUNKSIZE
