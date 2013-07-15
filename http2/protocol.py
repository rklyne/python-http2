

class Protocol(object):
    """Changable part of a connection. i
    Says how to:
    * interpret wire input
    * handle messages
    """
    def __init__(self,
        name, # like "HTTP/1/1", "HTTP-draft-01/2.0"
        stream_format, # reads/writes messages on a stream
        message_handler, # interprets messages
    ):
        self.name = name
        self.stream_format = stream_format
        self.message_handler = message_handler

    def serve_connection(self, connection, timeout=5):
        stream = connection.get_stream()
        while not stream.is_closed():
            message = self.stream_format.read_request_from_stream(stream, timeout=timeout)
            response = self.message_handler.handle_request(message, connection)
            self.stream_format.write_response_to_stream(response, stream)

    def read_request_message(self, stream):
        return self.stream_format.read_request_from_stream(stream)

    def send_request_message(self, message, stream):
        return self.stream_format.write_request_to_stream(message, stream)

    def read_response_message(self, stream):
        return self.stream_format.read_response_from_stream(stream)

    def send_response_message(self, message, stream):
        return self.stream_format.write_response_to_stream(message, stream)

    def get_name(self):
        return self.name

    def make_headers(self, *t, **k):
        return self.stream_format.make_headers(*t, **k)

    def make_request_message(self, *t, **k):
        return self.stream_format.make_request_message(*t, **k)

    def make_response_message(self, *t, **k):
        return self.stream_format.make_response_message(*t, **k)

