
class Dispatcher(object):
    def __init__(self):
        self.reset()

    # Control methods
    def reset(self):
        self.requests = []

    def assertCalled(self):
        assert self.requests, "dispatcher was not called"

    def assertNotCalled(self):
        assert not self.requests, "dispatcher was called"

    # Fake methods
    def handle(self, request):
        self.requests.append(request)

