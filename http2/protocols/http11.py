import http2


class Http11StreamFormat(http2.StreamFormat):
    NL = "\r\n"
#    def __init__(self, message_class=Message): 
#        self.message_class = message_class
    def write_request_to_stream(self, request, stream):
        import cStringIO as StringIO
        s = StringIO.StringIO()
        s.write(request.method)
        s.write(" ")
        s.write(request.url)
        s.write(" ")
        s.write(request.protocol_name)
        s.write(self.NL)
        self.write_headers(request.headers, s)
        stream.write(s.getvalue())
        if request.body is not None:
            stream.write(request.body)
        stream.flush()
        stream.done_sending()

    def read_request_from_stream(self,
        stream,
        timeout=5,
    ):
        
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
  
    def read_headers(self, 
        stream,
        timeout=5,
    ):
        assert hasattr(stream, 'pushback'), (stream, dir(stream))
        
        chunk = 32 *1024
        nl = "\r\n"
        len_nl = len(nl)
        buff = stream.read(chunk, timeout)
        headers_list = []
        while buff:
            nl_pos = buff.find(nl)
            if nl_pos < 0:
                new_buff = stream.read(chunk, timeout)
                if not new_buff:
                    raise RuntimeError("socket closed?", buff, new_buff)
                buff = buff + new_buff
                continue
            header, buff = buff[:nl_pos], buff[nl_pos+len_nl:]
            if header == "":
                stream.pushback(buff)
                return self.headers_class(headers_list)
            header_key, header_value = header.split(":", 1)
            header_key = header_key.strip()
            header_value = header_value.strip()
            headers_list.append((header_key, header_value))
        # Failing, but tidy up on our way out...
        stream.pushback(buff)
        raise ValueError("Headers not found in stream")
        return self.headers_class(headers_dict)

    def read_body(self, headers, stream, timeout=5):
        clen = int(headers.get('content-length', 0))
        body = ''
        import time
        end_time = time.time() + timeout
        while len(body) < clen:
            body += stream.read(clen)
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

    def write_response_to_stream(self,
        response,
        stream,
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
        stream.write(s.getvalue())
        if response.body is not None:
            stream.write(response.body)
        stream.flush()
    
    def read_response_from_stream(self,
        stream,
        timeout=5,#s
    ):
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
        request = http2.Request(method, url, headers, body)
        response = connection.dispatch_request(request)
        return response
        
    def handle_response(self, message, connection):
        raise NotImplementedError

Http11 = http2.Protocol(
    'HTTP/1.1',
    Http11StreamFormat(),
    Http11MessageHandler(),
)

class Http11Server(http2.Server):
    def __init__(self, dispatcher):
        super(Http11Server, self).__init__(Http11, dispatcher)
    
class Http11Client(http2.Client):
    def __init__(self, *t, **k):
        super(Http11Client, self).__init__(Http11, *t, **k)
            
    
