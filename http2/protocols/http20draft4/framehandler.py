

class FrameHandler(object):
    def __init__(self, 
        stream,
        frame_dispatcher,
        timeout=5,
        mode='response',
    ):
        import headers
        self.stream = stream
        self.dispatcher = frame_dispatcher
        self.timeout = timeout
        if mode == 'response':
            self.header_decoder = headers.ResponseHeaderDecompressor()
            self.header_encoder = headers.ResponseHeaderCompressor()
        elif mode == 'request':
            self.header_decoder = headers.RequestHeaderDecompressor()
            self.header_encoder = headers.RequestHeaderCompressor()
        else:
            raise ValueError(mode)
        self.header_buffers = {}
        self.push_promise_buffers = {}

    def handle_one(self):
        import frame
        data = self.read_frame()
        if data.type_id == frame.FRAME_SETTINGS:
            self.handle_settings(data)
        elif data.type_id == frame.FRAME_DATA:
            self.handle_data(data)
        elif data.type_id == frame.FRAME_HEADERS:
            self.handle_headers(data)
        elif data.type_id == frame.FRAME_PRIORITY:
            self.handle_priority(data)
        elif data.type_id == frame.FRAME_RST_STREAM:
            self.handle_stream_reset(data)
        elif data.type_id == frame.FRAME_PUSH_PROMISE:
            self.handle_push_promise(data)
        elif data.type_id == frame.FRAME_PING:
            self.handle_ping(data)
        elif data.type_id == frame.FRAME_WINDOWUPDATE:
            self.handle_window_update(data)
        elif data.type_id == frame.FRAME_GOAWAY:
            self.handle_goaway(data)
        else:
            self.dispatcher.handle_unknown_frame(data)

    def handle_data(self, frame):
        import struct
        # no flags defined
        data = frame.payload
        closed = bool(frame.flags & 1)
        self.dispatcher.write_data(frame.stream_id, data)
        if closed:
            self.dispatcher.close(frame.stream_id, 0)

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

    def handle_headers(self, frame):
        end_stream = bool(frame.flags & 1)
        end_headers = bool(frame.flags & 4)
        priority = bool(frame.flags & 8)
        data = frame.payload
        if priority:
            priority_val, data = data[:4], data[4:]
            priority_val = struct.unpack("!i", priority_val)
            self.dispatcher.set_priority(frame.stream_id, priority_val)
        self.header_buffers.setdefault(frame.stream_id, '')
        self.header_buffers[frame.stream_id] += data
        if end_headers:
            # process_buffered_headers
            data = self.header_buffers[frame.stream_id]
            headers = self.read_header_block(data)
            self.dispatcher.set_headers(frame.stream_id, headers)

    def read_header_block(self, data):
        return self.header_decoder.decode(data)

    def handle_priority(self, frame):
        import struct
        priority = struct.unpack("!i", frame.payload)[0]
        self.dispatcher.set_priority(frame.stream_id, priority)

    def handle_stream_reset(self, frame):
        import struct
        error_code = struct.unpack("!I", frame.payload)[0]
        self.dispatcher.close(frame.stream_id, error_code)

    def handle_push_promise(self, frame):
        import struct
        end_headers = bool(frame.flags & 1)
        promise = struct.unpack("!i", frame.payload[:4])[0]
        data = frame.payload[4:]
        self.push_promise_buffers.setdefault(frame.stream_id, '')
        self.push_promise_buffers[frame.stream_id] += data
        if end_headers:
            # process_buffered_headers
            data = self.push_promise_buffers[frame.stream_id]
            headers = self.read_header_block(data)
            self.dispatcher.set_headers(promise, headers)
            self.dispatcher.promised(promise)

    def handle_ping(self, frame):
        assert len(frame.payload) == 8
        if frame.flags & 1:
            self.dispatcher.pong(frame.stream_id, frame.payload)
        else:
            self.dispatcher.ping(frame.stream_id, frame.payload)

    def handle_goaway(self, frame):
        import struct
        data = frame.payload
        last_stream, error_code = struct.unpack("!iI", data[:8])
        debug_data = data[8:]
        self.dispatcher.go_away(last_stream, error_code, debug_data)

    def handle_window_update(self, frame):
        import struct
        increment = struct.unpack("!i", frame.payload)[0]
        self.dispatcher.window_update(frame.stream_id, increment)

    def handle_unknown_frame(self, frame):
        self.dispatcher.handle_unknown_frame(frame)

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


