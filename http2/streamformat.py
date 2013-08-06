import message

class StreamFormat(object):
    def __init__(self, 
        protocol,
        headers_class=message.Headers,
    ):
        self.name = protocol.get_name()
        self.protocol = protocol
        self.headers_class = headers_class

    def get_name(self):
        return self.name

    def initialise_state(self):
        return None

    def make_request_message(self, *t, **k):
        return message.RequestMessage(*t, **k)

    def make_response_message(self, *t, **k):
        return message.ResponseMessage(*t, **k)

    def write_request_to_stream(self, message, stream):
        raise NotImplementedError

    def write_response_to_stream(self, message, stream):
        raise NotImplementedError

    def read_request_from_stream(self, stream):
        raise NotImplementedError

    def read_response_from_stream(self, stream):
        raise NotImplementedError


