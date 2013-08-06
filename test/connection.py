import unittest

class FakeProtocol(object):
    pass
    

class TestConnection(unittest.TestCase):
    def setUp(self):
        import fakes
        self.stream = fakes.Stream("")
        self.dispatcher = fakes.Dispatcher()

    def test_request(self):
        pass
