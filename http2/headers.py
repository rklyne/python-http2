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
        if not isinstance(name, str):
            raise TypeError(name)
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

    def __iter__(self):
        for x in self.original_list:
            yield x

    def __contains__(self, item):
        if not hasattr(item, 'lower'):
            return False
        return item.lower() in self.header_values

