

class Request(object):
    def __init__(self, method, url, headers, body):
        self.method = method
        self.headers = headers
        self.body = body
        self.url = url
        
         
