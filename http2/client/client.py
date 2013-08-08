
class ClientConnection(object):
    def __init__(self, message_stream, protocol):
        self.message_stream = message_stream
        self.protocol = protocol
        import http2
        self.request_message_class = http2.RequestMessage

    def get(self, url, headers):
        assert headers is not None, "headers cannont be None"
        method = 'get'
        message = self.request_message_class(method, url, self.protocol.get_name(), headers, None)
        self.message_stream.send_request(message)
        response = self.message_stream.read_response()
        assert response, (self.message_stream, message)
        return response


class Client(object):
    def __init__(self,
        protocol,
        connection_class=None,
        headers_class=None,
        timeout=5,#s
    ):
        import http2
        if connection_class is None:
            connection_class = http2.ClientConnection
        self.connection_class = connection_class
        if headers_class is None:
            headers_class = http2.Headers
        self.headers_class = headers_class
        self.conn = None
        self.protocol = protocol
        self.timeout = timeout

    def close(self):
        if self.conn:
            self.conn.close()

    def default_headers(self):
        headers = []
        headers.append(('user-agent', 'Python-http2.Client'))
        return self.headers_class(headers)

    def get_connection(self, url_string):
        raise RuntimeError("deprecated")
        import urlparse, socket
        url = urlparse.urlparse(url_string)
        sock = socket.socket()
        try:
            sock.connect((url.hostname, url.port))
        except:
            sock.close()
        self.conn = self.connection_class(sock, self.protocol, timeout=self.timeout)
        return self.conn

    def open_stream(self, host, port):
        import socket
        sock = socket.socket()
        try:
            sock.connect((host, port))
            import http2.stream
            return http2.stream.PushbackStream(sock)
        except:
            sock.close()
            raise

    def connect_url(self, url_string):
        import urlparse
        url = urlparse.urlparse(url_string)
        stream = self.open_stream(url.hostname, url.port)
        return self.protocol.open_client(stream)
        #reader = self.protocol.read_stream(stream)
        #return ClientConnection(reader, self.protocol)

    # Convenience
    def get(self, url, headers=None):
        conn = self.connect_url(url)
        if headers is None:
            headers = self.default_headers()
        return conn.get(url, headers)

