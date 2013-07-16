
FRAME_DATA = 0
FRAME_HEADERS = 1
FRAME_PRIORITY = 2
FRAME_RST_STREAM = 3
FRAME_SETTINGS = 4
FRAME_PUSH_PROMISE = 5
FRAME_PING = 6
FRAME_GOAWAY = 7
FRAME_WINDOWUPDATE = 9

class Frame(object):
    def __init__(self, type_id, flags, stream_id, payload):
        assert isinstance(type_id, int)
        assert isinstance(flags, int)
        assert isinstance(stream_id, int)
        assert stream_id >= 0, "negative values can't be encoded."
        assert isinstance(payload, str)
        self.type_id = type_id
        self.flags = flags
        self.stream_id = stream_id
        self.payload = payload

    def get_length(self):
        return len(self.payload)

    def as_bytes(self):
        import struct
        import cStringIO as StringIO
        s = StringIO.StringIO()
        # the little 'i' serves to protect our reserved bit
        s.write(struct.pack("!HBBi", 
            self.get_length(),
            self.type_id,
            self.flags,
            self.stream_id,
        ))
        s.write(self.payload)
        return s.getvalue()
    
    @classmethod
    def from_bytes(cls, data):
        import struct
        if len(data) < 8:
            raise RuntimeError(data)
        length, type_id, flags, stream_id = struct.unpack("!HBBi", data[0:8])
        assert stream_id >= 0
        payload = data[8:]
        payload_len = len(payload)
        assert payload_len == length, (length, payload_len)
        return cls(type_id, flags, stream_id, payload)


