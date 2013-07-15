
class Server(object):
    def __init__(self, protocol, dispatcher):
        self.protocol = protocol
        self.dispatcher = dispatcher
        from http2 import ServerConnection
        self.connection_class = ServerConnection
        self.conns = []
        self.stopped = False
        self.sock = None

    def serve(self, addr='', port=80, timeout=5):
        if self.sock:
            raise RuntimeError()
        import socket
        self.sock = socket.socket()
        ACCEPT_TIMEOUT = 0.2#s
        self.sock.settimeout(ACCEPT_TIMEOUT)
        try:
            self.sock.bind((addr, port))
        except IOError:
            raise
            raise RuntimeError("bad address", addr, port)
        self.sock.listen(10)
        self._serve_connection(self.sock, timeout=timeout)

    def stop(self):
        self.stopped = True
        # Stop listening
        self.sock.close()

    def _serve_connection(self, sock, timeout=5):
        import socket
        while not self.stopped:
            try:
                new_sock, addr = sock.accept()
            except socket.timeout:
                pass
            else:
                self.add_connection(new_sock, timeout)

    def add_connection(self, new_sock, timeout):
        new_conn = self.connection_class(new_sock, self.protocol, self.dispatcher, timeout=timeout)
        new_conn.start_thread()
        self.conns.append(new_conn)


