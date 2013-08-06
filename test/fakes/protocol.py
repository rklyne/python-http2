
import http2

class FakeStreamFormat(object):
    def __init__(self, protocol):
        self.protocol = protocol
        self.p = protocol

        # Record what was done to us:
        self.requests_written = []
        self.responses_written = []
        self.requests_to_read = []
        self.responses_to_read = []
        # Arbitrary data
        import time
        self.state = time.time() - 10022

    def initialise_state(self):
        return self.state

    def check_state(self, state):
        assert self.state == state, "Wrong state obj"

    def write_request_to_stream(self, rq, stream, state):
        self.check_state(state)
        self.requests_written.append(rq)

    def write_response_to_stream(self, rsp, stream, state):
        self.check_state(state)
        self.responses_written.append(rsp)

    def read_request_from_stream(self, stream, state):
        self.check_state(state)
        if not self.requests_to_read:
            raise RuntimeError("Test did not provide any more requests")
        return self.requests_to_read.pop()

    def read_response_from_stream(self, stream, state):
        self.check_state(state)
        if not self.responses_to_read:
            raise RuntimeError("Test did not provide any more responses")
        return self.responses_to_read.pop()

class FakeMessageHandler(object):
    pass

class FakeProtocol(object):
    def __init__(self):
        self.requests = []
        self.responses = {}
    def get_name(self):
        return "HTTP/Test"
    def serve_stream(self, stream, dispatcher):
        data = stream.read()
        while self.requests:
            req = self.requests.pop()
            resp = dispatcher.handle_request(req)
            self.responses[req] = resp
            stream.write("a")
    def open_client(self, stream):
        raise RuntimeError(stream)
        
FakeProtocol = FakeProtocol()
#FakeProtocol = http2.protocol.Protocol(
#    "HTTP/Test",
#    FakeStreamFormat,
#    FakeMessageHandler,
#)
Protocol = FakeProtocol

class FakeProtocolReader(object):
    def __init__(self, protocol):
        self.protocol = protocol
        self.p = protocol

