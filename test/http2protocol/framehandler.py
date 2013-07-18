import unittest
import fakes

class FrameDispatcher(object):
    def __init__(self):
        self.settings = {}
        self.data = {}
        self.closed = {}
        self.headers = {}
        self.priorities = {}
        self.errors = {}

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

    def handle_unknown_frame(self, frame):
        raise RuntimeError(frame)

    def set_headers(self, stream, headers):
        self.headers[stream] = headers

    def get_priority(self, stream):
        return self.priorities[stream]

    def set_priority(self, stream, priority):
        self.priorities[stream] = priority

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
        self.failUnless(stream_id in dispatcher.data, "%s not in %s" %(stream_id, dispatcher.data.keys()))
        data = dispatcher.data[stream_id]
        self.assertEqual(data, "00070080000a0001".decode("hex"))
        self.failUnless(dispatcher.was_closed(stream_id),
            "did not close stream")

class TestPriorityFrame(unittest.TestCase):
    def get_single_frame(self):
        return """
        00 04 02 00 00 00 00 09
        00 00  00 10
        """.replace(" ", "").replace("\n", "").decode("hex")
    
    def get_stream(self, data):
        import http2
        return http2.PushbackStream(fakes.Stream(data))

    def test_priority_frame(self):
        import http2.protocols.http20draft4 as http20
        dispatcher = FrameDispatcher()
        frame = self.get_single_frame()
        stream = self.get_stream(frame)
        handler = http20.FrameHandler(stream, dispatcher)
        handler.handle_one()
        stream_id = 9
        self.assertEqual(
            dispatcher.get_priority(stream_id),
            16,
        )

class TestFrame(unittest.TestCase):
    def get_stream(self, data):
        import http2
        return http2.PushbackStream(fakes.Stream(data))

    def setUp(self):
        import http2.protocols.http20draft4 as http20
        self.dispatcher = FrameDispatcher()
        self.frame = self.get_single_frame()
        self.stream = self.get_stream(self.frame)
        self.handler = http20.FrameHandler(self.stream, self.dispatcher)
        self.handler.handle_one()

class TestRstStream(TestFrame):
    def get_single_frame(self):
        return """
        00 04 03 00 00 00 00 09
        00 00  00 01
        """.replace(" ", "").replace("\n", "").decode("hex")
    
    def test_stream_is_closed(self):
        stream_id = 9
        self.failUnless(self.dispatcher.was_closed(stream_id))
        self.assertEquals(self.dispatcher.errors.get(stream_id), 1)


class TestHeadersFrame(unittest.TestCase):
    def get_single_frame(self):
        return """
        00 05 01 04 00 00 00 05
        44 02 61 61
        80
        """.replace(" ", "").replace("\n", "").decode("hex")
    
    def get_stream(self, data):
        import http2
        return http2.PushbackStream(fakes.Stream(data))

    def test_headers_frame(self):
        import http2.protocols.http20draft4 as http20
        dispatcher = FrameDispatcher()
        self.failIf(dispatcher.data)
        frame = self.get_single_frame()
        stream = self.get_stream(frame)
        handler = http20.FrameHandler(stream, dispatcher)
        handler.handle_one()
        stream.sock.assertFinished()
        self.failUnless(dispatcher.headers)
        stream_id = 5
        self.failUnless(stream_id in dispatcher.headers, "%s not in %s" %(stream_id, dispatcher.headers.keys()))
        headers = dispatcher.headers[stream_id]
        self.assertEqual(len(headers), 2, headers.headers)
        self.assertEqual(headers.getall(':status'), ['200'])
        self.assertEqual(headers.getall('content-length'), [u'aa'])
        self.failIf(dispatcher.was_closed(stream_id),
            "closed stream")



