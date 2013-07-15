import unittest

from fakestream import *

class Http11ReadTests(unittest.TestCase):
    def setUp(self):
        self.stream_data = """GET / HTTP/1.1
User-Agent: Not specified

""".replace("\n", "\r\n")
    
    def make_stream(self, data):
        from http2 import PushbackStream
        if "\r\n" in data:
            pass
        elif "\n" in data:
            data = data.replace("\n", "\r\n")
        return PushbackStream(FakeStream(data))

    def test_reading_stream(self):
        from http2.protocols.http11 import Http11
        stream = self.make_stream(self.stream_data)
        self.failUnless(stream.read(1024), stream.sock.data)
        req = Http11.stream_format.read_request_from_stream(self.make_stream(self.stream_data), timeout=0.5)
        self.assertReqMatchesSent(req)

    def assertReqMatchesSent(self, req):
        self.assertEqual(req.method.lower(), 'get')
        self.assertEqual(req.url, '/')
        self.assertEqual(req.protocol_name, 'HTTP/1.1')
        self.assertEqual(len(req.headers), 1, req.headers.__dict__)
        self.assertEqual(req.headers.get('user-agent'), 'Not specified')
        self.assertEqual(req.body, '')

    def test_reading_stream_twice(self):
        from http2.protocols.http11 import Http11
        # Double data!
        stream = self.make_stream(self.stream_data+self.stream_data)
        self.failUnless(stream.read(1024), stream.sock.data)
        req = Http11.stream_format.read_request_from_stream(self.make_stream(self.stream_data), timeout=0.5)
        self.assertReqMatchesSent(req)
        req2 = Http11.stream_format.read_request_from_stream(self.make_stream(self.stream_data), timeout=0.5)
        self.assertReqMatchesSent(req2)

    def make_read_buffer(self):
        return self.make_stream("")

    def test_writing_stream(self):
        from http2.protocols.http11 import Http11
        stream = self.make_stream(self.stream_data)
        self.failUnless(stream.read(1024), stream.sock.data)
        stream = self.make_read_buffer()
        request = Http11.make_request_message(
            "GET",
            "/",
            "HTTP/1.1",
            Http11.make_headers([
                ("User-Agent", "Not specified"),
            ]),
            None
        )
        Http11.stream_format.write_request_to_stream(request, stream)
        stream_data = stream.sock.get_written_data()
        self.assertEqual(stream_data, self.stream_data)


