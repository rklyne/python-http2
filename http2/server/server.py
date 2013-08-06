
class Server(object):
    def __init__(self, protocol, dispatcher):
        self.protocol = protocol
        self.dispatcher = dispatcher
        #from http2 import ServerConnection
        #self.connection_class = ServerConnection
        #self.conns = []
        self.stopped = False
        self.sock = None
        self.server = None
        self.stream_manager_class = StreamManager
        self.streams = []

    def serve(self, addr='', port=80, timeout=5):
        import http2.sockets
        def handler(stream):
            self.add_stream(stream)
        self.server = http2.sockets.Server(addr, port, handler)
        self.server.start_serving()
        return
        assert isinstance(port, int), port
        assert isinstance(addr, str), addr
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
        self.sock.listen(0)
        self._serve_socket(self.sock, timeout=timeout)

    def serve_connection(self, timeout=5):
        raise RuntimeError("DeprecatedError")
        stream = self.get_stream()
        while not stream.is_closed():
            message = self.protocol.read_request()
            response = self.dispatch_request(message)
            self.protocol.send_response(response)
    
    def stop(self):
        self.stopped = True
        # Stop listening
        if self.server:
            self.server.stop()
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def _serve_socket(self, sock, timeout=5, accept_timeout=0.01):
        raise RuntimeError("DeprecatedError")
        import socket
        try:
            sock.settimeout(accept_timeout)
            while not self.stopped:
                try:
                    new_sock, addr = sock.accept()
                except socket.timeout:
                    pass
                else:
                    conn = self.add_connection(new_sock, timeout)
        finally:
            sock.close()

    def add_connection(self, new_sock, timeout):
        new_conn = self.connection_class(new_sock, self.protocol, timeout=timeout)
        self.conns.append(new_conn)
        new_conn.start_handling(self.dispatcher)
        return new_conn

    def add_stream(self, stream):
        manager = self.stream_manager_class(stream, self)
        self.streams.append(manager)
        manager.run()

    def remove_stream(self, stream):
        self.streams.remove(stream)

    def dispatch_request(self, request):
        return self.dispatcher.handle(request)

class StreamManager(object):
    def __init__(self, stream, server):
        self.stream = stream
        self.server = server
        self.protocol = server.protocol
        #self.message_reader = self.protocol.read_stream(self.stream)

    def run(self):
        try:
            stream = self.stream
            http_server = self.protocol.serve_stream(
                stream, 
                self, # as request dispatcher (handle_request())
            )
            #while not stream.is_closed():
                #message = self.message_reader.read_request()
                #response = self.dispatch_request(message)
                #self.message_reader.send_response(response)
                
        finally:
            self.stream.close()
            self.server.remove_stream(self)


    def dispatch_request(self, request):
        raise RuntimeError(request)
        return self.server.dispatch_request(request)

