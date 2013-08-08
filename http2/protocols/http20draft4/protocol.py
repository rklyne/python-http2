import http2
NAME = 'HTTP-draft-04/2.0'

class ServerFrameHandler(object):
    def __init__(self, dispatcher):
        self.request_dispatch = dispatcher

class ClientFrameHandler(object):
    pass

def request_stream_handler(stream, dispatcher):
    import framehandler
    frame_dispatch = ServerFrameHandler(dispatcher)
    handler = framehandler.FrameHandler(stream, frame_dispatch)
    raise NotImplementedError("Http2....")

def request_maker(stream, dispatcher):
    raise NotImplementedError("Http2....")

Http20d4 = http2.protocol.Protocol2(
    NAME,
    request_stream_handler,
    request_maker,
)

class Http20d4Server(http2.server.Server):
    def __init__(self, dispatcher):
        super(Http20d4Server, self).__init__(Http20d4, dispatcher)
    
class Http20d4Client(http2.client.Client):
    def __init__(self, *t, **k):
        super(Http20d4Client, self).__init__(Http20d4, *t, **k)
            
