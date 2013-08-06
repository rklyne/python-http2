
class FrameDispatcher(object):
    def __init__(self):
        self.settings = {}
        self.data = {}
        self.closed = {}
        self.headers = {}
        self.priorities = {}
        self.errors = {}
        self.pings = {}
        self.pongs = {}
        self.promises = {}
        self.goaway_data = []
        self.window = {}

    def new_settings(self, settings):
        for k, v in settings.items():
            assert isinstance(k, int), k
            assert k % int('0fff', 16) == k, k
            assert isinstance(v, int), v
            assert v % int('ffff', 16) == v, v
        self.settings.update(settings)

    def write_data(self, stream_id, data):
        self.data.setdefault(stream_id, '')
        self.data[stream_id] += data

    def close(self, stream_id, error_code=0):
        self.closed[stream_id] = True
        self.errors[stream_id] = error_code

    def was_closed(self, stream_id):
        return self.closed.get(stream_id)

    def go_away(self, last_stream, error_code, data):
        self.goaway_data.append((
            last_stream,
            error_code,
            data,
        ))

    def handle_unknown_frame(self, frame):
        raise RuntimeError(frame)

    def set_headers(self, stream, headers):
        self.headers[stream] = headers

    def get_priority(self, stream):
        return self.priorities[stream]

    def set_priority(self, stream, priority):
        self.priorities[stream] = priority

    def ping(self, stream_id, data):
        self.pings[stream_id] = data

    def pong(self, stream_id, data):
        self.pongs[stream_id] = data

    def promised(self, stream):
        self.promises[stream] = True

    def window_update(self, stream, increment):
        self.window.setdefault(stream, 0)
        self.window[stream] += increment

import protocol
import http2
class Http20d4Server(http2.server.Server):
    def __init__(self, dispatcher):
        super(Http20d4Server, self).__init__(protocol.Http20d4, dispatcher)


