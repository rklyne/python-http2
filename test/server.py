
import unittest
import fakes

class ServerTest(unittest.TestCase):
    def setUp(self):
        import http2
        self.dispatcher = fakes.Dispatcher()
        self.protocol = FakeProtocol()
        self.server = http2.server.Server(
            self.protocol,
            self.dispatcher,
        )
        self.port = 8092
        self.thread = None

    def tearDown(self):
        self.server.stop()
        if self.thread:
            self.thread.join()
    def test_creation(self):
        self.assertCannotConnect(self.port)
        self.failUnless(self.server)
        self.assertCannotConnect(self.port)

    def start_serving(self):
        if self.thread:
            self.thread.join()
        import threading
        self.thread = threading.Thread()
        self.thread.setName("Tst-"+self._testMethodName)
        def run(p=self.port):
            self.server.serve(port=p)
        self.thread.run = run
        self.thread.start()

    def test_listening(self):
        port = self.port
        self.assertCannotConnect(port)
        self.start_serving()
        self.assertCanConnect(port)

    def assertCannotConnect(self, port, timeout=0.2):
        import socket
        s = socket.socket()
        try:
            s.settimeout(timeout)
            try:
                s.connect(('localhost', port))
            except IOError, e:
                return
            else:
                self.fail("Could connect: " + str(port))
            # No assertions - it'll error or it won't
        finally:
            s.close()
    def assertCanConnect(self, port, timeout=0.2):
        import socket
        s = socket.socket()
        try:
            s.settimeout(timeout)
            try:
                s.connect(('localhost', port))
            except Exception, e:
                self.fail("Could not connect: " + str(e))
            # No assertions - it'll error or it won't
        finally:
            s.close()

    def test_stopping(self):
        self.start_serving()
        self.assertCanConnect(self.port)
        self.server.stop()
        self.thread.join()
        self.assertCannotConnect(self.port)

    def test_request_handling(self):
        stream = fakes.Stream("a")

if __name__ == '__main__':
    unittest.main()

class FakeProtocol(object):
    def __init__(self):
        self.requests = []
        self.responses = {}
        self.streams_served = []
    def get_name(self):
        return "HTTP/Test"
    def serve_stream(self, stream, dispatcher):
        self.streams_served.append(stream)
        while self.requests:
            req = self.requests.pop()
            resp = dispatcher.handle_request(req)
            self.responses[req] = resp
        #raise RuntimeError()
    def open_client(self, stream):
        raise RuntimeError(stream)
