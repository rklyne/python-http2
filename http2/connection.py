
class Connection(object):
    def __init__(self,
        socket,
        protocol,
        stream_class=None,
        timeout=5,
    ):
        self.socket = socket
        self.protocol = protocol
        self.timeout = timeout
        self.socket.settimeout(timeout)
        self.thread = None
        self.stream = None
        if stream_class is None:
            import http2
            stream_class = http2.PushbackStream
        self.stream_class = stream_class

    def process_connection_upgrade(self, request):
        upgrade_header = request.get_header('upgrade')
        raise NotImplementedError(upgrade_header)

    def get_stream(self):
        if self.stream is None:
            self.stream = self.stream_class(self.socket)
        return self.stream

    def send_request_message(self, message):
        self.protocol.send_request_message(message, self.get_stream())
        self.stream.done_sending()
        return self.protocol.read_response_message(self.get_stream())

    def send_request(self, request):
        raise RuntimeError("deprecated")
        stream = self.get_stream()
        self.protocol.write_request_to_stream(request, stream)
        
    def make_headers(self, *t, **k):
        return self.protocol.make_headers(*t, **k)

    def make_request_message(self, *t, **k):
        return self.protocol.make_request_message(*t, **k)

    def make_response_message(self, *t, **k):
        return self.protocol.make_response_message(*t, **k)

class ServerConnection(Connection):
    def __init__(self,
        socket,
        protocol,
        dispatcher,
        stream_class=None,
        timeout=5,
    ):
        super(ServerConnection, self).__init__(socket, protocol, stream_class=stream_class, timeout=timeout)
        self.dispatcher = dispatcher
    def start_thread(self):
        if self.thread:
            raise RuntimeError("Already running")
        import threading
        self.thread = threading.Thread()
        self.thread.run = self.run
        self.thread.setDaemon(True)
        self.thread.start()

    def run(self):
        try:
            self.protocol.serve_connection(self, self.timeout)
        except:
            stream_closed = self.get_stream().is_closed()
            self.socket.close()
            if not stream_closed:
                raise


    def dispatch_request(self, request):
        return self.dispatcher.handle(request, self)

class ClientConnection(Connection):
    def send_request(self, method, url, headers, body):
        import http2
        request = http2.RequestMessage(method, url, headers, body)
        self.send_message(request)
        raise NotImplementedError


