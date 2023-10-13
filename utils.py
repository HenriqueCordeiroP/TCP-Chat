PORT = 443
IP = '127.0.0.1'
BUFFER_SIZE = 1024

import zlib

def compute_checksum(data):
    checksum = 0
    try:
        data = data.decode("ascii")
    except AttributeError:
        pass
    for char in data:
        checksum ^= ord(char)
    return checksum