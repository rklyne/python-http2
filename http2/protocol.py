
class MessageStream(object):
    def __init__(self, stream, formatter):
        self.stream = stream
        self.formatter = formatter
        self.state = formatter.initialise_state()

    def read_request(self, **k):
        return self.formatter.read_request_from_stream(self.stream, self.state, **k)

    def send_request(self, message, **k):
        assert not k, k
        return self.formatter.write_request_to_stream(message, self.stream, self.state, **k)

    def read_response(self, **k):
        return self.formatter.read_response_from_stream(self.stream, self.state, **k)

    def send_response(self, message, **k):
        return self.formatter.write_response_to_stream(message, self.stream, self.state, **k)


    #read_response_from_stream = read_response
    #write_response_to_stream = send_response
    #read_request_from_stream = read_request
    #write_request_to_stream = send_request



class ProtocolReader(object):
    def __init__(self, stream, protocol):
        self.stream = stream
        self.protocol = protocol
        self.stream_format = protocol.stream_format_class(stream)
        try:
            self.message_handler = protocol.message_handler_class()
        except Exception, e:
            raise RuntimeError(str(e), protocol, protocol.message_handler_class)

    def serve_connection(self, connection, timeout=5):
        stream = connection.get_stream()
        while not stream.is_closed():
            message = self.stream_format.read_request_from_stream(stream, timeout=timeout)
            response = self.message_handler.handle_request(message, connection)
            self.stream_format.write_response_to_stream(response, stream)


#    def make_headers(self, *t, **k):
#        return self.protocol.make_headers(*t, **k)
#
#    def make_request_message(self, *t, **k):
#        return self.protocol.make_request_message(*t, **k)
#
#    def make_response_message(self, *t, **k):
#        return self.protocol.make_response_message(*t, **k)
#
    def get_protocol_name(self):
        return self.protocol.get_name()

class Protocol(object):
    """Changable part of a connection. i
    Says how to:
    * interpret wire input
    * handle messages
    """
    def __init__(self,
        name, # like "HTTP/1.1", "HTTP-draft-01/2.0"
        stream_format, # reads/writes messages on a stream
        message_handler, # interprets messages
        request_class=None,
        response_class=None,
    ):
        raise RuntimeError("Deprecated")
        self.name = name
        assert isinstance(stream_format, type), `stream_format`
        self.stream_format_class = stream_format
        self.stream_format = self.stream_format_class(self)
        assert isinstance(message_handler, type), `message_handler`
        self.message_handler_class = message_handler
#        if request_class is None:
#            import http2.message
#            request_class = http2.message.RequestMessage
#        if response_class is None:
#            import http2.message
#            response_class = http2.message.ResponseMessage
#        self.request_class = request_class
#        self.response_class = response_class
#        self.headers_class = http2.Headers

    def get_name(self):
        return self.name

    def initialise_state(self):
        return self.stream_format.initialise_state()

    def read_stream(self, stream):
        return MessageStream(stream, self.stream_format)
        return ProtocolReader(
            stream,
            self,
        )
    
    def serve_stream(self, stream, dispatcher, threaded = False):
        
        server = ProtocolStreamServer(stream, self, dispatcher)
        if threaded:
            server.start()
        else:
            server.run()
        return
        state = self.initialise_state()
        reader = self.read_stream(stream)
        while not stream.is_closed():
            request = self.stream_format.read_request_from_stream(stream, state)
            assert request
            #message = reader.read_request()
            response = dispatcher.dispatch_request(request)
            self.stream_format.write_response_to_stream(response, stream, state)
            #reader.send_response(response)
            stream.close()

    def open_client(self, stream):
        raise NotImplementedError("TODO: return an object with a make_request method")

#    def make_headers(self, *t, **k):
#        return self.headers_class(*t, **k)
#
#    def make_request_message(self, *t, **k):
#        return self.request_class(*t, **k)
#
#    def make_response_message(self, *t, **k):
#        return self.response_class(*t, **k)
#

import threading
class ProtocolStreamServer(threading.Thread):
    def __init__(self, stream, protocol, dispatcher):
        super(ProtocolStreamServer, self).__init__()
        self.stream = stream
        self.protocol = protocol
        self.dispatcher = dispatcher

    def run(self):
        self.protocol.request_maker(self.stream, self.dispatcher)
        return
        stream = self.stream
        state = self.protocol.initialise_state()
        reader = self.protocol.read_stream(stream)
        while not stream.is_closed():
            request = self.protocol.stream_format.read_request_from_stream(stream, state)
            assert request
            response = dispatcher.dispatch_request(request)
            assert response
            self.protocol.stream_format.write_response_to_stream(response, stream, state)

class HttpClient(object):
    def get(self, url):
        return
    def post(self, url, data):
        return
    def make_request(self, url, method, postdata):
        import http2.message
        request = http2.message.RequestMessage(url, method, headers, postdata)
        self.request_maker(request)

class Protocol2(object):
    """Changable part of a connection. i
    Says how to:
    * interpret wire input
    * handle messages
    """
    def __init__(self,
        name, # like "HTTP/1.1", "HTTP-draft-01/2.0"
        request_handler, # given a stream, handles requests
        request_maker, # Sends requests and returns responses.
    ):
        self.name = name
        assert callable(request_handler), `request_handler`
        assert callable(request_maker), `request_maker`
        self.request_maker = request_maker
        self.request_handler = request_handler

    def serve_stream(self, stream, dispatcher, threaded=True):
        server = ProtocolStreamServer(stream, self, dispatcher)
        if threaded:
            server.start()
        else:
            server.run()

    def open_client(self, stream):
        return HttpClient(stream, self.request_maker)


