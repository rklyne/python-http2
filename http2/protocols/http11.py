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
        if not hasattr(request, 'method'):
            raise ValueError(request)
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
        
        method, url, proto = self.read_request_line(timeout=timeout)
        assert proto == NAME, proto
        headers = self.read_headers(timeout=timeout)
        body = ''
        method = method.upper()
        if method not in ('GET', 'HEAD', 'DELETE'):
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
            buff = self.stream.read(chunk, timeout=timeout)
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
        return method.upper(), url, protocol_name
  
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

    def read_body(self,
        headers,
        read_to_eof=False,
        timeout=5,
    ):
        from http2.errors import ProtocolError
        len_header = 'content-length'
        if len_header in headers:
            clen = int(headers.get(len_header))
        elif read_to_eof:
            clen = None
        else:
            raise RuntimeError("missing content-length", headers.__dict__, self.stream.__dict__)
            raise ProtocolError, "Missing required 'content-length' header"
        import cStringIO as StringIO
        body = StringIO.StringIO()
        import time
        end_time = time.time() + timeout
        if clen is None:
            chunk = 32*1024
            while self.stream.has_input:
                body.write(self.stream.read(chunk, timeout=timeout))
        else:
            while body.tell() < clen:
                body.write(self.stream.read(clen, timeout=timeout))
        return body.getvalue()

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
        allowed_body=True,
        timeout=5,#s
    ):
        buff = self.stream.read(1024, timeout=timeout)
        if not buff:
            import time
            time.sleep(0.1)
            raise RuntimeError(timeout, self.stream.read(100), self.stream.__dict__)
        nl_pos = buff.find(self.NL)
        assert nl_pos > 0, `buff`
        status_line, buff = buff[:nl_pos], buff[nl_pos+len(self.NL):]
        status_code, status_message = status_line.split(' ', 1)
        status_code = int(status_code)
#        raise RuntimeError(status_code, status_message, buff)
        self.stream.pushback(buff)
        headers = self.read_headers(timeout=timeout)
        body = ''
        if allowed_body:
            body = self.read_body(
                headers,
                read_to_eof=True,
                timeout=timeout,
            )
        resp = self.make_response_message(
            status_code, 
            status_message, 
            headers, 
            body,
        )
        assert resp, status_line
        return resp

def http11_request_handler(stream, dispatcher, timeout=5):
    assert hasattr(dispatcher, 'handle'), dispatcher
    http_stream = Http11Stream(stream)
    request = http_stream.read_request(timeout=timeout)
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
            
    
