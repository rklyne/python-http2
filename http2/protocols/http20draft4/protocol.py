import http2
NAME = 'HTTP-draft-04/2.0'

class Http20d4StreamFormat(http2.streamformat.StreamFormat):
    """A HTTP 1.1 TCP stream
    """

    NL = "\r\n"
    def __init__(self,  *t, **k): 
        super(Http20d4StreamFormat, self).__init__(*t, **k)

    def init_context(self):
        from http2.protocols.http2 import FrameHandler
        return {
            'framehandler': FrameHandler(),
        }

    def write_request_to_stream(self, request, stream, state):
        
        raise NotImplementedError("Make this http/2.0")

    def read_request_from_stream(self,
        stream,
        state,
        timeout=5,
    ):
        raise NotImplementedError("Make this http/2.0")
        
        method, url, proto = self.read_request_line(stream)
        headers = self.read_headers(stream, timeout=timeout)
        body = self.read_body(headers, stream)
        return self.make_request_message(
            method,
            url,
            proto,
            headers,
            body,
        )

    def read_request_line(self, stream, read_wait=0.02, timeout=5):
        line = ''
        chunk = 1024
        pos = -1
        first_buff = None
        import time
        end_time = time.time() + timeout
        while pos < 0:
            buff = stream.read(chunk)
            if not buff:
                time.sleep(read_wait)
                if time .time() > end_time:
                    raise RuntimeError("timeout", line)
                continue
            if first_buff is None:
                first_buff = buff
            line = line + buff
            pos = line.find(self.NL)
        line, rest = line[:pos], line[pos+len(self.NL):]
        stream.pushback(rest)
        full_line = line
        assert ' ' in line, (full_line, first_buff)
        method, line = line.split(' ', 1)
        assert ' ' in line, (full_line, first_buff)
        url, protocol_name = line.rsplit(' ', 1)
        return method, url, protocol_name
  
    def write_response_to_stream(self,
        response,
        stream,
        state,
    ):
        raise NotImplementedError("Make this http/2.0")
        import cStringIO as StringIO
        s = StringIO.StringIO()
        # Response line
        s.write(str(response.status_code))
        s.write(" ")
        s.write(response.status_message)
        s.write(self.NL)

        # Headers
        self.write_headers(response.headers, s)

        # And write out...
        stream.write(s.getvalue())
        if response.body is not None:
            stream.write(response.body)
        stream.flush()
    
    def read_response_from_stream(self,
        stream,
        state,
        timeout=5,#s
    ):
        raise NotImplementedError("Make this http/2.0")
        buff = stream.read(1024)
        nl_pos = buff.find(self.NL)
        assert nl_pos > 0, buff
        status_line, buff = buff[:nl_pos], buff[nl_pos+len(self.NL):]
        status_code, status_message = status_line.split(' ', 1)
        status_code = int(status_code)
#        raise RuntimeError(status_code, status_message, buff)
        stream.pushback(buff)
        headers = self.read_headers(stream, timeout=timeout)
        body = self.read_body(headers, stream, timeout=timeout)
        return self.make_response_message(
            status_code, 
            status_message, 
            headers, 
            body,
        )
        raise NotImplementedError

class Http20d4MessageHandler(object):
    def handle_request(self, message):
        # Process control messages
        pass
        # Pass request to dispatcher
        #raise RuntimeError(message.__dict__)
        method = message.method
        headers = message.headers
        body = message.body
        url = message.url
        request = http2.request.Request(method, url, headers, body)
        response = self.connection.dispatch_request(request)
        return response
        
    def handle_response(self, message, connection):
        raise NotImplementedError

def request_stream_handler(stream, dispatcher):
    
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
            
