
class Frame(object):
    def __init__(self, header, body):
        assert isinstance(header, str)
        assert isinstance(body, str)

