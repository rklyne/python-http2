import unittest

class TestPushbackStream(unittest.TestCase):
    def stream(self, data):
        from fakes import *
        s = FakeStream(data)
        return s

    def test_pushback(self):
        import http2
        data_in = "data stream"
        sock = self.stream(data_in)
        s = http2.PushbackStream(sock)
        self.failUnless(s.has_input)
        d = s.read(100)
        # Check we got the data
        self.failUnless(d)

        half_data = d[5:]
        s.pushback(half_data)
        self.failUnless(s.has_input)

        d2 = s.read(100)
        self.assertEqual(d2, half_data)


    def test_read_all(self):
        import http2
        data_in = "data stream"
        s = http2.PushbackStream(self.stream(data_in))
        self.failUnless(s.has_input)
        d = s.read(100)
        # Need to read again to find out that the socket is empty.
        # ... sockets eh?
        d2 = s.read(1, timeout=0.01)
        self.failIf(d2, "data should be gone by now")
        self.failIf(s.has_input, "should not have input left after reading")


