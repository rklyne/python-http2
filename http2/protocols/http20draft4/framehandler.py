

class FrameHandler(object):
    def __init__(self, 
        stream,
        frame_dispatcher,
        timeout=5,
    ):
        self.stream = stream
        self.dispatcher = frame_dispatcher
        self.timeout = timeout

    def handle_one(self):
        import frame
        data = self.read_frame()
        if data.type_id == frame.FRAME_SETTINGS:
            self.handle_settings(data)
        elif data.type_id == frame.FRAME_DATA:
            self.handle_data(data)
        else:
            self.dispatcher.handle_unknown_frame(frame)

    def handle_data(self, frame):
        import struct
        # no flags defined
        data = frame.payload
        closed = bool(frame.flags & 1)
        self.dispatcher.write_data(frame.stream_id, data, closed)

    def handle_settings(self, frame):
        import struct
        # no flags defined
        data = frame.payload
        settings = {}
        start = 0
        dlen = len(data)
        bytes_per_setting = 4
        assert dlen % bytes_per_setting == 0, (dlen, data)
        while start < dlen:
            new_setting = data[start:start+bytes_per_setting]
            key, value = struct.unpack("!HH", new_setting)
            settings[key] = value
            start += bytes_per_setting
        self.dispatcher.new_settings(settings)
    def handle_unknown_frame(self, frame):
        raise RuntimeError(frame)

    def read_frame(self):
        import frame as Frame
        import struct
        import cStringIO as StringIO
        buff = StringIO.StringIO()
        len_header = self.stream.read(2)
        assert len(len_header) == 2, len_header
        frame_len = struct.unpack("!H", len_header)[0]
        buff.write(len_header)
        # There are more bytes to read here
        read = -6
        while read < frame_len:
            target = frame_len - read
            tmp = self.stream.read(target, timeout=self.timeout)
            buff.write(tmp[:target])
            if len(tmp) > target:
                self.stream.pushback(tmp[target:])
            read += len(tmp)
        frame_data = buff.getvalue()
        assert len(frame_data) == frame_len+8, (frame_len, frame_data)
        return Frame.Frame.from_bytes(frame_data)


