import unittest

class TestHttp11ServerRequests(unittest.TestCase):
    def test_serving_requests(self):
        self.assertStreamRequest(
        "GET / HTTP/1.1\r\n\r\n", 
        "GET", "/", {}, '')

    def test_headers(self):
        self.assertStreamRequest(
        "GET / HTTP/1.1\r\nxxx:yyy\r\n\r\n", 
        "GET", "/", {'xxx': ['yyy']}, '')

    def test_post(self):
        self.assertStreamRequest(
        "POST / HTTP/1.1\r\nContent-length:5\r\n\r\ndata!", 
        "POST", "/", {'Content-length': ['5']}, 'data!')

    def assertStreamRequest(self,
        stream_data,
        method,
        url,
        headers,
        body,
    ):
        import fakes
        socket = fakes.Stream(stream_data)
        import http2.stream
        stream = http2.stream.PushbackStream(socket)
        dispatcher = fakes.Dispatcher()
        import http2.protocols.http11
        http2.protocols.http11.http11_request_handler(stream, dispatcher)
        dispatcher.assertWasCalled()
        request = dispatcher.get_request()
        self.assertEqual(request.method, method)
        self.assertEqual(request.url, url)
        self.assertEqual(request.body, body)
        for header, values in headers.items():
            actual_values = request.headers.get_all(header)
            self.assertEqual(len(actual_values), len(values))
            for v in values:
                assert v in actual_values, "%s missing value %s" %(header, v)

class TestHttp11ServerResponses(unittest.TestCase):
    def assertStreamResponse(self,
        stream_data,
        code,
        message,
        headers_dict,
        body,
    ):
        import fakes
        socket = fakes.Stream("GET / HTTP/1.1\r\n\r\n")
        import http2.stream
        stream = http2.stream.PushbackStream(socket)
        import http2.message
        headers_lst = []
        for k, vs in headers_dict.items():
            for v in vs:
                headers_lst.append((k, v))
        headers = http2.message.Headers(headers_lst)
        response = http2.message.ResponseMessage(code, message, headers, body)
        dispatcher = fakes.Dispatcher(response=response)

        import http2.protocols.http11
        http2.protocols.http11.http11_request_handler(stream, dispatcher)
        dispatcher.assertWasCalled()
        data = socket.get_written_data()
        self.assertEqual(data, stream_data)

    def test_simple(self):
        self.assertStreamResponse(
            "200 OK\r\nContent-length: 2\r\n\r\nhi",
            200, "OK", {'Content-length':['2']},
            "hi",
        )
    
    def test_100_continue(self):
        self.assertStreamResponse(
            "100 continue...\r\n\r\n",
            100, "continue...", {},
            "",
        )

    def test_no_headers(self):
        self.assertStreamResponse(
            "200 OK\r\n\r\nhi",
            200, "OK", {},
            "hi",
        )

def make_headers(data):
    import http2.message
    if isinstance(data, dict):
        headers_lst = []
        for k, vs in data.items():
            for v in vs:
                headers_lst.append((k, v))
        return http2.message.Headers(headers_lst)
    elif isinstance(data, list):
        return http2.message.Headers(data)
    else:
        raise ValueError(`data`, type(data))
    
class TestHttp11ClientRequest(unittest.TestCase):
    def assertRequestStream(self,
        stream_data,
        method,
        url,
        headers_dict,
        body,
    ):
        import fakes
        # Don't care about the response
        socket = fakes.Stream("200 OK\r\n\r\n")
        import http2.stream
        stream = http2.stream.PushbackStream(socket)
        headers = make_headers(headers_dict)
        request = http2.message.RequestMessage(method, url, headers, body)

        import http2.protocols.http11
        response = http2.protocols.http11.http11_request_maker(stream, request)
        data = socket.get_written_data()
        self.assertEqual(data, stream_data)

    def test_simple_get(self):
        self.assertRequestStream(
            "GET / HTTP/1.1\r\n\r\n",
            "GET", "/", {}, ""
        )

    def test_simple_post(self):
        self.assertRequestStream(
            "POST / HTTP/1.1\r\n\r\n",
            "POST", "/", {}, ""
        )

    def test_get_with_headers(self):
        self.assertRequestStream(
            "GET / HTTP/1.1\r\nxx: yy\r\nzz: 1\r\nzz: 2\r\n\r\n",
            "GET", "/",
            [('xx','yy'), ('zz', '1'), ('zz','2')],
            ""
        )

class TestHttp11ClientResponse(unittest.TestCase):
    def assertStreamResponse(self,
        stream_data,
        code,
        message,
        headers_dict,
        body,
    ):
        import fakes
        # Don't care about the response
        socket = fakes.Stream(stream_data)
        import http2.stream
        stream = http2.stream.PushbackStream(socket)
        request = http2.message.RequestMessage(
            "GET", "/",
            http2.message.Headers([]), ""
        )

        import http2.protocols.http11
        response = http2.protocols.http11.http11_request_maker(stream, request)
        data = socket.get_written_data()
        self.assertEqual(response.status_code, code)
        self.assertEqual(response.status_message, message)
        self.assertEqual(response.body, body)
        for header, values in headers_dict.items():
            actual_values = response.headers.get_all(header)
            self.assertEqual(len(actual_values), len(values))
            for v in values:
                assert v in actual_values, "%s missing value %s" %(header, v)

    def test_simple(self):
        self.assertStreamResponse(
            "2000 Yes\r\n\r\n",
            2000, "Yes", {}, ""
        )

    def test_body_without_content_length(self):
        self.assertStreamResponse(
            "2000 Yes\r\n\r\nwords",
            2000, "Yes", {}, "words"
        )

    def test_body_with_content_length(self):
        self.assertStreamResponse(
            "2000 Yes\r\ncontent-length:5\r\n\r\nwords",
            2000, "Yes", {}, "words"
        )

    def test_headers(self):
        self.assertStreamResponse(
            "2000 Yes\r\nx:y\r\nz:1\r\nz:2\r\n\r\n",
            2000, "Yes", {'x':['y'], 'z': ['1','2']}, ""
        )

