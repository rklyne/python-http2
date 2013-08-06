import http2

NAME = 'HTTP/1.1'

class Http11Stream(object):
    """A HTTP 1.1 TCP stream
    """

    NL = "\r\n"
    def __init__(self, stream): 
        assert hasattr(stream, 'pushback'), (stream, dir(stream))
        self.stream = stream
        import http2.message
        self.headers_class = http2.message.Headers
        self.make_request_message = http2.message.RequestMessage
        self.make_response_message = http2.message.ResponseMessage

    def write_request(self, request):
        import cStringIO as StringIO
        s = StringIO.StringIO()
        s.write(request.method)
        s.write(" ")
        s.write(request.url)
        s.write(" ")
        s.write(NAME)
        s.write(self.NL)
        self.write_headers(request.headers, s)
        self.stream.write(s.getvalue())
        if request.body is not None:
            self.stream.write(request.body)
        self.stream.done_sending()

    def read_request(self,
        timeout=5,
    ):
        
        method, url, proto = self.read_request_line()
        assert proto == NAME, proto
        headers = self.read_headers(timeout=timeout)
        body = self.read_body(headers)
        return self.make_request_message(
            method,
            url,
            headers,
            body,
        )

    def read_request_line(self, read_wait=0.02, timeout=5):
        line = ''
        chunk = 1024
        pos = -1
        first_buff = None
        import time
        end_time = time.time() + timeout
        while pos < 0:
            buff = self.stream.read(chunk)
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
        self.stream.pushback(rest)
        full_line = line
        assert ' ' in line, (full_line, first_buff)
        method, line = line.split(' ', 1)
        assert ' ' in line, (full_line, first_buff)
        url, protocol_name = line.rsplit(' ', 1)
        return method, url, protocol_name
  
    def read_headers(self, 
        timeout=5,
    ):
        
        chunk = 32 *1024
        nl = "\r\n"
        len_nl = len(nl)
        buff = self.stream.read(chunk, timeout)
        headers_list = []
        while buff:
            nl_pos = buff.find(nl)
            if nl_pos < 0:
                new_buff = self.stream.read(chunk, timeout)
                if not new_buff:
                    raise RuntimeError("socket closed?", buff, new_buff)
                buff = buff + new_buff
                continue
            header, buff = buff[:nl_pos], buff[nl_pos+len_nl:]
            if header == "":
                self.stream.pushback(buff)
                return self.headers_class(headers_list)
            header_key, header_value = header.split(":", 1)
            header_key = header_key.strip()
            header_value = header_value.strip()
            headers_list.append((header_key, header_value))
        # Failing, but tidy up on our way out...
        self.stream.pushback(buff)
        raise ValueError("Headers not found in stream")
        return self.headers_class(headers_dict)

    def read_body(self, headers, timeout=5):
        len_header = 'content-length'
        if len_header in headers:
            clen = int(headers.get(len_header))
        else:
            clen = None
        body = ''
        import time
        end_time = time.time() + timeout
        if clen is None:
            chunk = 32*1024
            while not self.stream.is_closed():
                body += self.stream.read(chunk)
                if time.time() > end_time:
                    raise RuntimeError("read_body timeout", len(body), clen, body)
        else:
            while len(body) < clen:
                body += self.stream.read(clen)
                if time.time() > end_time:
                    raise RuntimeError("read_body timeout", len(body), clen, body)
        return body

    def write_headers(self, headers, s):
        for k, v in headers.all_headers():
            s.write(k)
            s.write(": ")
            s.write(v)
            s.write(self.NL)
        s.write(self.NL)

    def write_response(self,
        response,
    ):
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
        self.stream.write(s.getvalue())
        if response.body is not None:
            self.stream.write(response.body)
        self.stream.flush()
    
    def read_response(self,
        timeout=5,#s
    ):
        buff = self.stream.read(1024)
        nl_pos = buff.find(self.NL)
        assert nl_pos > 0, buff
        status_line, buff = buff[:nl_pos], buff[nl_pos+len(self.NL):]
        status_code, status_message = status_line.split(' ', 1)
        status_code = int(status_code)
#        raise RuntimeError(status_code, status_message, buff)
        self.stream.pushback(buff)
        headers = self.read_headers(timeout=timeout)
        body = self.read_body(headers, timeout=timeout)
        return self.make_response_message(
            status_code, 
            status_message, 
            headers, 
            body,
        )

class Http11MessageHandler(object):
    def handle_request(self, message, connection):
        # Process control messages
        pass
        # Pass request to dispatcher
        #raise RuntimeError(message.__dict__)
        method = message.method
        headers = message.headers
        body = message.body
        url = message.url
        request = http2.request.Request(method, url, headers, body)
        response = connection.dispatch_request(request)
        return response
        
    def handle_response(self, message, connection):
        raise NotImplementedError

def http11_request_handler(stream, dispatcher):
    http_stream = Http11Stream(stream)
    request = http_stream.read_request()
    response = dispatcher.handle(request)
    assert response, request
    http_stream.write_response(response)

def http11_request_maker(stream, request):
    http_stream = Http11Stream(stream)
    http_stream.write_request(request)
    response = http_stream.read_response()
    return response
    

Http11 = http2.protocol.Protocol2(
    NAME,
    http11_request_handler,
    http11_request_maker,
)

class Http11Server(http2.server.Server):
    def __init__(self, dispatcher):
        super(Http11Server, self).__init__(Http11, dispatcher)
    
class Http11Client(http2.client.Client):
    def __init__(self, *t, **k):
        super(Http11Client, self).__init__(Http11, *t, **k)
            
    
