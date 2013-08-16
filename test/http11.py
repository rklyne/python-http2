

import unittest


TEST_TIMEOUT = 0.5 # seconds
class EndToEndHttp11Tests(unittest.TestCase):
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
        self.thread.setName("Tst-http11-"+self._testMethodName)
        self.port = 8096
        def f(self=self):
            self.server.serve(port=self.port, timeout=TEST_TIMEOUT)
        self.thread.run = f
        self.thread.start()
        import time
        time.sleep(0.01)
        return "http://localhost:8096/"

    def setUp(self):
        from http2 import Http11Server, Http11Client, Wsgi
        wsgi = self.get_simple_wsgi()
        server = Http11Server(Wsgi(wsgi))
        self.server = server
        
        client = Http11Client(timeout=TEST_TIMEOUT)
        self.client = client

        self.thread = None

    def tearDown(self):
        self.server.stop()
        if self.thread:
            self.thread.join()

    def test_http11_request(self):
        server_url = self.start_serving_thread()
        resp = self.client.get(server_url)
        self.failUnless(resp)



