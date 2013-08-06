import protocol
import http2
class Http20d4Client(http2.client.Client):
    def __init__(self, *t, **k):
        super(Http20d4Client, self).__init__(protocol.Http20d4, *t, **k)

