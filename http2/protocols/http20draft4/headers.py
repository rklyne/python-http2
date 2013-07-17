
from headertable import *

class Headers(object):
    def __init__(self):
        self.headers = {}

    def add(self, key, value):
        self.headers.setdefault(key, []).append(value)

    def has(self, key):
        return key in self.headers
    __contains__ = has

    def keys(self):
        return self.headers.keys()

    def getall(self, key):
        return self.headers[key]

    def __len__(self):
        return sum(map(len, self.headers.values()))

class HeaderTokeniser(object):
    SEVEN_BITS = int('01111111', 2)

    def __init__(self, data):
        self.data = data
        self.cursor = 0
        self.finished = (len(data) == 0)
    
    def read_bytes(self, count):
        end = self.cursor + count
        new = self.data[self.cursor:end]
        self.cursor = end
        if self.cursor >= len(self.data):
            self.finished = True
        assert len(new) == count, "Header block depleted prematurely"
        return new

    def read_byte_as_int(self):
        return ord(self.read_bytes(1))

    def read_int(self, prefix, first_byte):
        assert 0 <= prefix < 8, prefix
        mask = (2 ** prefix) - 1
        value = first_byte & mask
        if value < mask:
            return value
        next_byte = first_byte
        if prefix != 0:
            next_byte = self.read_byte_as_int()
        top_bit = 2 ** 7
        m = 0
        while True:
            # read another byte
            value += (next_byte & self.SEVEN_BITS) << m
            m += 7
            # raise RuntimeError(value, next_byte)
            if next_byte & top_bit:
                next_byte = self.read_byte_as_int()
            else:
                break
        return value

    def read_string(self):
        count = self.read_int(0, self.read_byte_as_int())
        return self.read_bytes(count).decode('utf8')

    def has_more(self):
        return not self.finished

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
    SIX_BITS_MASK = int('00111111',2)

    def __init__(self):
        # TODO: get a differnet table for requests + responses
        self.init_table()
        self.last_headers = Headers()

    def init_table(self):
        raise NotImplementedError("abstract method")

    def decode(self, data):
        block_headers = Headers()
        tokens = HeaderTokeniser(data)
        while tokens.has_more():
            first_byte_cursor = tokens.cursor
            first_byte = tokens.read_byte_as_int()
            if first_byte & self.INDEXED_HEADER_MASK:
                # b) index header repr
                header_num = first_byte & self.FIVE_BITS_MASK
                name, value = self.table.get_by_index(header_num)
                block_headers.add(name, value)
            elif first_byte & self.LITERAL_HEADER_MASK:
                # a) literal header
                indexed = not bool(first_byte & self.UNINDEXED_LITERAL_MASK)
                header_num = tokens.read_int(5, first_byte)
                #header_num = first_byte & self.FIVE_BITS_MASK
                if header_num == 0:
                    # Not indexed at all
                    name = tokens.read_string()
                else:
                    header_num -= 1
                    try:
                        name, _ = self.table.get_by_index(header_num)
                    except IndexError:
                        raise RuntimeError("bad num", header_num, len(self.table), tokens.cursor, tokens.data, tokens.data[first_byte_cursor:])
                value = tokens.read_string()
                if indexed:
                    self.table.add(name, value)
                block_headers.add(name, value)
            else:
                # (substitution indexing)
                header_num = tokens.read_int(6, first_byte)
                if header_num == 0:
                    name = tokens.read_string()
                else:
                    header_num -= 1
                    name, _ = self.table.get_by_index(header_num)
                new_num = tokens.read_int(0, tokens.read_byte_as_int())
                #raise RuntimeError(tokens, first_byte, name, header_num, tokens.cursor, tokens.data)
                value = tokens.read_string()
                try:
                    self.table.replace(new_num, name, value)
                except IndexError:
                    raise RuntimeError("bad num", header_num, len(self.table), tokens.cursor, tokens.data, tokens.data[first_byte_cursor:])
                block_headers.add(name, value)
            # c) differential coding
        self.last_headers = block_headers
        return block_headers

class RequestHeaderCompressor(HeaderCompressor):
    def init_table(self):
        self.table = HeaderTable("request")

class ResponseHeaderCompressor(HeaderCompressor):
    def init_table(self):
        self.table = HeaderTable("response")

class RequestHeaderDecompressor(HeaderDecompressor):
    def init_table(self):
        self.table = HeaderTable("request")

class ResponseHeaderDecompressor(HeaderDecompressor):
    def init_table(self):
        self.table = HeaderTable("response")

