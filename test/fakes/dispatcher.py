
class Dispatcher(object):
    def __init__(self, response=None):
        if response is None:
            import http2.message
            headers = http2.message.Headers([])
            response = http2.message.ResponseMessage(200, "OK", headers, "")
        self.response = response
        self.reset()

    # Control methods
    def reset(self):
        self.requests = []

    def assertCalled(self):
        assert self.requests, "dispatcher was not called"
    assertWasCalled = assertCalled

    def assertNotCalled(self):
        assert not self.requests, "dispatcher was called"

    def get_request(self, idx=0):
        return self.requests[idx]

    # Fake methods
    def handle(self, request):
        self.requests.append(request)
        return self.response


