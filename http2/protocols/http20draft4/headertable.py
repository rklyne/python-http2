

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

    def __len__(self):
        return len(self.lst)

    def replace(self, num, k, v):
        oldk, oldv = self.lst[num]
        del self.map[oldk]
        self.lst[num] = (k, v)
        self.map[k] = num

    def init_response(self):
        self.add(u":status", u"200", 0)
        self.add(u"age", u"", 1 )    
        self.add(u"cache-control", u"", 2 )    
        self.add(u"content-length", u"", 3 )    
        self.add(u"content-type", u"", 4)
        self.add(u"date", u"", 5)
        self.add(u"etag", u"", 6)
        self.add(u"expires", u"", 7)
        self.add(u"last-modified", u"", 8)
        self.add(u"server", u"", 9)
        self.add(u"set-cookie", u"", 10)
        self.add(u"vary", u"", 11)
        self.add(u"via", u"", 12)
        self.add(u"access-control-allow-origin", u"", 13)
        self.add(u"accept-ranges", u"", 14)
        self.add(u"allow", u"", 15)
        self.add(u"connection", u"", 16)
        self.add(u"content-disposition", u"", 17)
        self.add(u"content-encoding", u"", 18)
        self.add(u"content-language", u"", 19)
        self.add(u"content-location", u"", 20)
        self.add(u"content-md5", u"", 21)
        self.add(u"content-range", u"", 22)
        self.add(u"link", u"", 23)
        self.add(u"location", u"", 24)
        self.add(u"p3p", u"", 25)
        self.add(u"pragma", u"", 26)
        self.add(u"proxy-authenticate", u"", 27)
        self.add(u"refresh", u"", 28)
        self.add(u"retry-after", u"", 29)
        self.add(u"strict-transport-security", u"", 30)
        self.add(u"trailer", u"", 31)
        self.add(u"transfer-encoding", u"", 32)
        self.add(u"warning", u"", 33)
        self.add(u"www-authenticate", u"", 34)

    def init_request(self):
        self.add(u':scheme', u'http', 0)
        self.add(u':scheme', u'https', 1)
        self.add(u':host', u'', 2)
        self.add(u':path', u'/', 3)
        self.add(u':method get', u'', 4)
        self.add(u'accept', u'', 5)
        self.add(u'accept-charset', u'', 6)
        self.add(u'accept-encoding', u'', 7)
        self.add(u'accept-language', u'', 8)
        self.add(u'cookie', u'', 9)
        self.add(u'if-modified-since', u'', 10)
        self.add(u'keep-alive', u'', 11)
        self.add(u'user-agent', u'', 12)
        self.add(u'proxy-connection', u'', 13)
        self.add(u'referer', u'', 14)
        self.add(u'accept-datetime', u'', 15)
        self.add(u'authorization', u'', 16)
        self.add(u'allow', u'', 17)
        self.add(u'cache-control', u'', 18)
        self.add(u'connection', u'', 19)
        self.add(u'content-length', u'', 20)
        self.add(u'content-md5', u'', 21)
        self.add(u'content-type', u'', 22)
        self.add(u'date', u'', 23)
        self.add(u'expect', u'', 24)
        self.add(u'from', u'', 25)
        self.add(u'if-match', u'', 26)
        self.add(u'if-none-match', u'', 27)
        self.add(u'if-range', u'', 28)
        self.add(u'if-unmodified-since', u'', 29)
        self.add(u'max-forwards', u'', 30)
        self.add(u'pragma', u'', 31)
        self.add(u'proxy-authorization', u'', 32)
        self.add(u'range', u'', 33)
        self.add(u'te', u'', 34)
        self.add(u'upgrade', u'', 35)
        self.add(u'via', u'', 36)
        self.add(u'warning', u'', 37)

    def add(self, name, value, at_index=None):
        assert isinstance(name, unicode), `name`
        assert isinstance(value, unicode), `value`
        i = len(self.lst)
        if at_index is not None:
            if i != at_index:
                raise RuntimeError("not at expected index", i, at_index)
        self.lst.append((name, value))
        self.map[name] = i
        return i

    def get_by_index(self, idx):
        try:
            return self.lst[idx]
        except IndexError:
            raise IndexError(idx, len(self.lst))
    def get_by_name(self, name):
        raise RuntimeError("NotSupported. Should not come up...")
        return self.lst[self.map[name]]



