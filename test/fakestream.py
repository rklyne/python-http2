import unittest

__all__ = [
    'FakeStream',
]
class FakeStream(object):
    def __init__(self, data):
        self.data = data
    def recv(self, count):
        result, self.data= self.data[:count], self.data[count:]
        return result

    def setblocking(self, value):
        assert value == 0, "We're faking non-blocking."

    def settimeout(self, value):
        # It's a fake...
        # We don't do any waiting, so no timeout problems :-)
        return

    def close(self):
        self.data = ""

class FakeStreamTests(unittest.TestCase):
    def test_fake_stream(self):
        data_in = "data stream"
        s = FakeStream(data_in)
        d = s.recv(100)
        # Check we got the data
        self.failUnless(d, s.data)
        # Check the fake has no more data
        self.failIf(s.data, d)
        # Check we got the right data
        self.assertEqual(d, data_in)





