
class Wsgi(object):
    def __init__(self, wsgi_func):
        self.wsgi_func = wsgi_func

    def handle(self, request, connection=None):
        import thread
        ready_lock = thread.allocate_lock()
        ready_lock.acquire()
        env = {}
        env['method'] = request.method
        env['url'] = request.url
        response = []
        def start_response(status, headers_list, body=None):
            code, message = status.split(' ', 1)
            code = int(code)
            headers = self.make_headers(headers_list)
            response_obj = self.make_response_message(
                code,
                message,
                headers,
                body,
            )
            response.append(response_obj)
            ready_lock.release()
        self.wsgi_func(env, start_response)

        ready_lock.acquire()
        assert response, response
        return response[0]

    def make_response_message(self, *t, **k):
        import http2
        return http2.ResponseMessage(*t, **k)

    def make_headers(self, *t, **k):
        import http2
        return http2.Headers(*t, **k)

