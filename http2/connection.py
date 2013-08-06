
class Connection(object):
    """Wraps a socket and presents messages.
    """
    def __init__(self,
        stream,
        protocol,
        stream_class=None,
        timeout=5,
    ):
        self.timeout = timeout
        self.socket.settimeout(timeout)
        self.thread = None
        self.stream = stream
        self.protocol = None
        self.set_protocol(protocol)

    def process_connection_upgrade(self, request):
        upgrade_header = request.get_header('upgrade')
        raise NotImplementedError(upgrade_header)

    def set_protocol(self, protocol):
        if self.protocol:
            self.protocol.wrap_up_comms()
        self.protocol_setting = protocol
        self.protocol = protocol.read_stream(self.get_stream())

    def close(self):
        self.stream.close()

    def get_stream(self):
        if self.stream is None:
            self.stream = self.stream_class(self.socket)
        return self.stream

    def send_request_message(self, message):
        self.protocol.send_request_message(message)
        self.stream.done_sending()
        return self.protocol.read_response_message()

    def send_request(self, request):
        raise RuntimeError("deprecated")
        stream = self.get_stream()
        self.protocol.write_request(request, stream)
        
    def make_headers(self, *t, **k):
        import http2
        return http2.Headers(*t, **k)
        return self.protocol.make_headers(*t, **k)

    def make_request_message(self, *t, **k):
        import http2.message
        return http2.message.RequestMessage(*t, **k)

    def make_response_message(self, *t, **k):
        import http2.message
        return http2.message.ResponseMessage(*t, **k)

class ServerConnection(Connection):
    def __init__(self,
        socket,
        message_reader,
        stream_class=None,
        timeout=5,
    ):
        super(ServerConnection, self).__init__(socket, message_reader, stream_class=stream_class, timeout=timeout)
    def start_thread(self):
        if self.thread:
            raise RuntimeError("Already running")
        import threading
        self.thread = threading.Thread()
        self.thread.run = self.run
        self.thread.setDaemon(True)
        self.thread.start()

    def start_handling(self, dispatcher):
        if self.threaded:
            self.start_thread()
    def _handle(self, dispatcher):
        stream = self.get_stream()
        while not stream.is_closed():
            message = self.protocol.read_request()
            response = dispatcher.handle(message)
            self.protocol.send_response(response)
        
    def run(self):
        try:
            self.serve_connection(self.timeout)
        except:
            stream_closed = self.get_stream().is_closed()
            self.socket.close()
            if not stream_closed:
                raise


class ClientConnection(Connection):
    def send_request(self, method, url, headers, body):
        import http2
        request = http2.RequestMessage(method, url, headers, body)
        self.send_message(request)
        raise NotImplementedError


