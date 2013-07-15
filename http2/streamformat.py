import http2

class StreamFormat(object):
    def __init__(self, 
        request_message_class=http2.RequestMessage,
        response_message_class=http2.ResponseMessage,
        headers_class=http2.Headers,
    ):
        self.request_message_class = request_message_class 
        self.response_message_class = response_message_class 
        self.headers_class = headers_class

    def make_request_message(self, *t, **k):
        return self.request_message_class(*t, **k)

    def make_response_message(self, *t, **k):
        return self.response_message_class(*t, **k)

    def make_headers(self, *t, **k):
        return self.headers_class(*t, **k)

    def write_request_to_stream(self, message, stream):
        raise NotImplementedError

    def write_response_to_stream(self, message, stream):
        raise NotImplementedError

    def read_request_from_stream(self, stream):
        raise NotImplementedError

    def read_response_from_stream(self, stream):
        raise NotImplementedError


