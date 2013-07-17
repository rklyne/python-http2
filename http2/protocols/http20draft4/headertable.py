

class HeaderTable(object):
    def __init__(self, type):
        self.lst = []
        self.map = {}
        t = type.lower()
        if t == 'request':
            self.init_request()
        elif t == 'response':
            self.init_response()
        else:
            raise ValueError(type)

    def init_response(self):
        self.add(":status", "200", 0)
        self.add("age", "", 1 )    
        self.add("cache-control", "", 2 )    
        self.add("content-length", "", 3 )    
        self.add("content-type", "", 4)
        self.add("date", "", 5)
        self.add("etag", "", 6)
        self.add("expires", "", 7)
        self.add("last-modified", "", 8)
        self.add("server", "", 9)
        self.add("set-cookie", "", 10)
        self.add("vary", "", 11)
        self.add("via", "", 12)
        self.add("access-control-allow-origin", "", 13)
        self.add("accept-ranges", "", 14)
        self.add("allow", "", 15)
        self.add("connection", "", 16)
        self.add("content-disposition", "", 17)
        self.add("content-encoding", "", 18)
        self.add("content-language", "", 19)
        self.add("content-location", "", 20)
        self.add("content-md5", "", 21)
        self.add("content-range", "", 22)
        self.add("link", "", 23)
        self.add("location", "", 24)
        self.add("p3p", "", 25)
        self.add("pragma", "", 26)
        self.add("proxy-authenticate", "", 27)
        self.add("refresh", "", 28)
        self.add("retry-after", "", 29)
        self.add("strict-transport-security", "", 30)
        self.add("trailer", "", 31)
        self.add("transfer-encoding", "", 32)
        self.add("warning", "", 33)
        self.add("www-authenticate", "", 34)
    def add(self, name, value, at_index=None):
        assert isinstance(name, str), name
        assert isinstance(value, str), value
        i = len(self.lst)
        if at_index is not None:
            if i != at_index:
                raise RuntimeError("not at expected index", i, at_index)
        self.lst.append((name, value))
        self.map[name] = i
        return i

    def get_by_index(self, idx):
        return self.lst[idx]
    def get_by_name(self, name):
        return self.lst[self.map[name]]



