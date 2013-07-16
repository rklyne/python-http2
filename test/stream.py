import unittest

class TestPushbackStream(unittest.TestCase):
    def stream(self, data):
        from fakes import *
        s = FakeStream(data)
        return s

    def test_pushback(self):
        import http2
        data_in = "data stream"
        s = http2.PushbackStream(self.stream(data_in))
        d = s.read(100)
        # Check we got the data
        self.failUnless(d)

        half_data = d[5:]
        s.pushback(half_data)

        d2 = s.read(100)
        self.assertEqual(d2, half_data)





