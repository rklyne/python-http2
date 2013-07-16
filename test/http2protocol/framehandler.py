import unittest
import fakes

class FrameDispatcher(object):
    def __init__(self):
        self.settings = {}
        self.data = {}
        self.closed = {}

    def new_settings(self, settings):
        for k, v in settings.items():
            assert isinstance(k, int), k
            assert k % int('0fff', 16) == k, k
            assert isinstance(v, int), v
            assert v % int('ffff', 16) == v, v
        self.settings.update(settings)

    def write_data(self, stream_id, data, close=False):
        self.data.setdefault(stream_id, '')
        self.data[stream_id] += data
        self.closed[stream_id] = True

    def was_closed(self, stream_id):
        return self.closed.get(stream_id)

    def handle_unknown_frame(self, frame):
        raise RuntimeError(frame)

class TestSettingsFrame(unittest.TestCase):
    def get_frame(self):
        # An empty settings frame
        return """
        00 00 04 00 00 00 00 00
        """.replace(" ", "").replace("\n", "").decode("hex")
    
    def get_two_setting_frame(self):
        return """
        00 08 04 00 00 00 00 00
        00 07  00 80
        00 0a  00 01
        """.replace(" ", "").replace("\n", "").decode("hex")
    
    def get_stream(self, data):
        import http2
        return http2.PushbackStream(fakes.Stream(data))

    def test_two_setting_frame(self):
        import http2.protocols.http20draft4 as http20
        dispatcher = FrameDispatcher()
        self.failIf(dispatcher.settings)
        frame = self.get_two_setting_frame()
        stream = self.get_stream(frame)
        handler = http20.FrameHandler(stream, dispatcher)
        handler.handle_one()
        self.assertEqual(dispatcher.settings.get(10), 1)
        self.assertEqual(dispatcher.settings.get(7), 128)


    def test_empty_frame(self):
        import http2.protocols.http20draft4 as http20
        dispatcher = FrameDispatcher()
        frame = self.get_frame()
        stream = self.get_stream(frame)
        handler = http20.FrameHandler(stream, dispatcher)
        handler.handle_one()
        # Basically just testing that it doesn't error        

class TestDataFrame(unittest.TestCase):
    def get_single_frame(self):
        return """
        00 08 00 01 00 00 00 05
        00 07  00 80
        00 0a  00 01
        """.replace(" ", "").replace("\n", "").decode("hex")
    
    def get_stream(self, data):
        import http2
        return http2.PushbackStream(fakes.Stream(data))

    def test_data_frame(self):
        import http2.protocols.http20draft4 as http20
        dispatcher = FrameDispatcher()
        self.failIf(dispatcher.data)
        frame = self.get_single_frame()
        stream = self.get_stream(frame)
        handler = http20.FrameHandler(stream, dispatcher)
        handler.handle_one()
        self.failUnless(dispatcher.data)
        stream_id = 5
        self.failUnless(stream_id in dispatcher.data)
        data = dispatcher.data[stream_id]
        self.assertEqual(data, "00070080000a0001".decode("hex"))



