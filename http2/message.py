from http2.headers import Headers

class RequestMessage(object):
    type = 'request'
    def __init__(self,
        method,
        url,
        headers,
        body,
    ):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

class ResponseMessage(object):
    type = 'response'

    def __init__(self,
        status_code,
        status_message,
        headers,
        body,
    ):
        assert isinstance(status_code, int), status_code
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers
        self.body = body

    
