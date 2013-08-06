

import unittest


TEST_TIMEOUT = 0.5 # seconds
class EndToEndHttp20Tests(unittest.TestCase):
    RESPONSE = """Status: 200 OK
Content-Type: text/plain
Content-Length: 9

Hi there!"""
    def get_simple_wsgi(self):
        import wsgiref.simple_server
        # Hello world...
        return wsgiref.simple_server.demo_app

    def start_serving_thread(self):
        if self.thread:
            raise RuntimeError()
        import threading
        self.thread = threading.Thread()
        self.thread.setName("Tst-http20d4-"+self._testMethodName)
        self.port = 8091
        def f(self=self):
            self.server.serve(port=self.port, timeout=TEST_TIMEOUT)
        self.thread.run = f
        self.thread.start()
        import time
        time.sleep(0.01)
        return "http://localhost:8091/"

    def setUp(self):
        from http2 import Http20d4Server, Http20d4Client, Wsgi
        wsgi = self.get_simple_wsgi()
        server = Http20d4Server(Wsgi(wsgi))
        self.server = server
        
        client = Http20d4Client(timeout=TEST_TIMEOUT)
        self.client = client

        self.thread = None

    def tearDown(self):
        self.server.stop()
        if self.thread:
            self.thread.join()

    def test_http20_request(self):
        self.fail("not implemented")
        server_url = self.start_serving_thread()
        resp = self.client.get(server_url)
        self.failUnless(resp)



