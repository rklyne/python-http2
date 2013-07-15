
class RequestMessage(object):
    type = 'request'
    def __init__(self,
        method,
        url,
        protocol_name,
        headers,
        body,
    ):
        self.method = method
        self.url = url
        self.protocol_name = protocol_name
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

    
class Headers(object):
    def __init__(self,
        header_list,
    ):
        assert isinstance(header_list, list), header_list
        header_list = header_list[:]
        self.original_list = header_list
        self.header_values = {}
        for k, v in header_list:
            l = self.header_values.setdefault(k.lower(), [])
            l.append(v)

    def get(self, name, default=None):
        l = self.get_all(name)
        if l:
            assert len(l) == 1, l
            return l[0]
        return default
    def get_all(self, name):
        return self.header_values.get(name.lower(), [])

    __getitem__ = get

    def __len__(self):
        return len(self.original_list)

    def all_headers(self):
        return self.original_list


