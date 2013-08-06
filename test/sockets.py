import unittest
import http2.sockets

# Mock
class StreamHandler(object):
    def __init__(self):
        self.streams = []
    def handle(self, stream):
        stream.close()
        self.streams.append(stream)
    def assertStreamCount(self, n):
        assert len(self.streams) == n, len(self.streams)

class TestSocketServer(unittest.TestCase):
    PORT = 9871
    HOST = 'localhost'
    TIMEOUT = 0.0005

    def setUp(self):
        host = self.HOST
        port = self.PORT
        self.handler = StreamHandler()
        self.server = http2.sockets.Server(host, port, self.handler, new_socket_timeout=self.TIMEOUT)
    def tearDown(self):
        self.server.stop()
        import gc
        gc.collect()

    def test_serving(self):
        self.server.start_thread()
        import socket
        import time
        s = socket.socket()
        self.handler.assertStreamCount(0)
        s.connect((self.HOST, self.PORT))
        time.sleep(0.01)
        self.handler.assertStreamCount(1)
        s.close()
        self.handler.assertStreamCount(1)

    def test_closing(self):
        self.server.start_thread()
        self.server.stop()
        import socket
        import time
        s = socket.socket()
        self.handler.assertStreamCount(0)
        try:
            s.connect((self.HOST, self.PORT))
        except socket.error:
            pass
        else:
            s.close()
            self.fail("should have failed to connect")

    def test_closing_after_connection(self):
        import socket
        import time
        self.server.start_thread()
        # The first connection
        s = socket.socket()
        s.connect((self.HOST, self.PORT))
        s.close()
        # Then stop
        self.server.stop()
        # Then connect again
        s = socket.socket()
        try:
            s.connect((self.HOST, self.PORT))
        except socket.error:
            pass
        else:
            s.close()
            self.fail("should have failed to connect")

class TestSocketStream(unittest.TestCase):
    PORT = 9872
    def setUp(self):
        import http2.sockets
        self.host = 'localhost'
        self.port = self.PORT
        def stream_handler(stream):
            stream.write("banana")
            stream.close()
        self.server = http2.sockets.Server(self.host, self.port, stream_handler)
        self.server.start_thread()

    def tearDown(self):
        self.server.stop()

    def test_stream(self):
        import http2.sockets
        s = http2.sockets.Stream(self.host, self.port)
        data = s.read(6)
        s.close()
        self.assertEqual(data, "banana")
        

