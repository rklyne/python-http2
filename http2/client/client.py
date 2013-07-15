
class Client(object):
    def __init__(self,
        protocol,
        connection_class=None,
        headers_class=None,
        timeout=5,#s
    ):
        import http2
        self.request_message_class = http2.RequestMessage
        if connection_class is None:
            connection_class = http2.ClientConnection
        self.connection_class = connection_class
        if headers_class is None:
            headers_class = http2.Headers
        self.headers_class = headers_class
        self.conn = None
        self.protocol = protocol
        self.timeout = timeout

    def default_headers(self):
        headers = []
        headers.append(('user-agent', 'Python-http2.Client'))
        return self.headers_class(headers)

    def get_connection(self, url_string):
        import urlparse, socket
        url = urlparse.urlparse(url_string)
        sock = socket.socket()
        try:
            sock.connect((url.hostname, int(url.port)))
        except:
            sock.close()
        return self.connection_class(sock, self.protocol, timeout=self.timeout)

    def get(self, url):
        conn = self.get_connection(url)
        headers = self.default_headers()
        method = 'get'
        message = self.request_message_class(method, url, self.protocol.get_name(), headers, None)
        response = conn.send_request_message(message)
        assert response, (conn, message)
        return response

