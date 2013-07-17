
from headertable import *

class Headers(object):
    def __init__(self):
        self.headers = {}

    def add(self, key, value):
        assert isinstance(key, int), key
        self.headers[key] = value

    def has(self, key):
        return key in self.headers
    __contains__ = has

    def keys(self):
        return self.headers.keys()

class HeaderTokeniser(object):
    SEVEN_BITS = int('01111111', 2)

    def __init__(self, data):
        self.data = data
        self.cursor = 0
    
    def read_bytes(self, count):
        end = self.cursor + count
        new = self.data[self.cursor:end]
        self.cursor = end
        return new

    def read_byte_as_int(self):
        return ord(self.read_bytes(1))

    def read_int(self, prefix=8, first_byte=None):
        assert 0 < prefix <= 8, prefix
        if prefix != 8:
            assert first_byte is not None
        if first_byte is None:
            first_byte = self.read_byte_as_int()
        assert isinstance(first_byte, int), first_byte
        value = 0
        top_bit = 2 ** (prefix-1)
        assert isinstance(top_bit, int), top_bit
        value = first_byte % top_bit
        last_byte = first_byte
        while last_byte & top_bit:
            # read another byte
            next_byte = self.read_byte_as_int()
            # raise RuntimeError(value, next_byte)
            value = (value << 7) + (next_byte & self.SEVEN_BITS)
            last_byte = next_byte
        return value

    def read_string(self):
        count = self.read_int()
        return self.read_bytes(count).decode('utf8')

class HeaderCompressor(object):
    def __init__(self):
        pass
    def encode(self, headers):
        raise NotImplementedError(headers)

class HeaderDecompressor(object):
    INDEXED_HEADER_MASK = int('10000000',2)
    LITERAL_HEADER_MASK = int('01000000',2)
    UNINDEXED_LITERAL_MASK = int('00100000',2)
    FIVE_BITS_MASK = int('00011111',2)

    def __init__(self):
        # TODO: get a differnet table for requests + responses
        self.init_table()

    def init_table(self):
        raise NotImplementedError("abstract method")

    def decode(self, data):
        block_headers = {}
        tokens = HeaderTokeniser(data)
        first_byte = tokens.read_byte_as_int()
        if first_byte & self.INDEXED_HEADER_MASK:
            # b) index header repr
            data = first_byte
            header_num = first_byte & self.FIVE_BITS_MASK
            name, value = self.table.get_by_index(header_num)
            block_headers[name] = value
        elif first_byte & self.LITERAL_HEADER_MASK:
            # a) literal header
            indexed = bool(first_byte & self.UNINDEXED_LITERAL_MASK)
            header_num = first_byte & self.FIVE_BITS_MASK
            if header_num == 0:
                # Not indexed at all
                name = tokens.read_string()
            else:
                name, _ = self.table.get_by_index(header_num)
            value = tokens.read_string()
            block_headers[name] = [value]
        else:
            raise RuntimeError
            # c) differential coding
        return block_headers

class RequestHeaderDecompressor(HeaderDecompressor):
    def init_table(self):
        self.table = HeaderTable("request")

class ResponseHeaderDecompressor(HeaderDecompressor):
    def init_table(self):
        self.table = HeaderTable("response")

