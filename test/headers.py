import unittest


class HeadersTest(unittest.TestCase):

    def test_contains_by_lower_case(self):
        import http2.headers
        h = http2.headers.Headers([
            ('X', 'val'),
            ('y', 'val'),
        ])
        self.failUnless('x' in h)
        self.failUnless('X' in h)
        self.failUnless('y' in h)
        self.failUnless('Y' in h)
    
    def test_get_by_lower_case(self):
        import http2.headers
        h = http2.headers.Headers([
            ('n', 1),
            ('N', 2),
        ])
        nums = [1,2]
        self.assertEquals(h.get_all('n'), nums)
        self.assertEquals(h.get_all('N'), nums)

