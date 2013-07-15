import unittest

from fakestream import *

class Http11ReadTests(unittest.TestCase):
    def setUp(self):
        self.stream_data = """200 OK
Content-Length: 4
Content-Type: text/plain

Hai!"""
    
    def make_stream(self, data):
        from http2 import PushbackStream
        if "\r\n" in data:
            pass
        elif "\n" in data:
            data = data.replace("\n", "\r\n")
        return PushbackStream(FakeStream(data))

    def test_reading_response_stream(self):
        from http2.protocols.http11 import Http11
        resp = Http11.stream_format.read_response_from_stream(self.make_stream(self.stream_data), timeout=0.5)
        self.assertResponseMatchesSent(resp)

    def assertResponseMatchesSent(self, resp):
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.status_message, "OK")
        self.assertEqual(len(resp.headers), 2, resp.headers.__dict__)
        self.assertEqual(resp.headers.get('content-type'), 'text/plain')
        self.assertEqual(resp.headers.get('content-length'), '4')
        self.assertEqual(resp.body, 'Hai!')



