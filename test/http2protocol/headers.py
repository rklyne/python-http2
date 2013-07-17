import unittest

class TestDecompressor(unittest.TestCase):
    def setUp(self):
        from http2.protocols.http20draft4 import ResponseHeaderDecompressor
        self.c = ResponseHeaderDecompressor()

    def test_read_simple(self):
        """
> var decompressor = new Decompressor('REQUEST');

> var headerblock1 = '44162f6d792d6578616d706c652f696e6465782e68746d6c4d0d6d792d757365722d6167656e' +
                     '74400b782d6d792d686561646572056669727374';

> decompressor.decompress(new Buffer(headerblock1, 'hex'));
{ ':path': '/my-example/index.html',
  'user-agent': 'my-user-agent',
  'x-my-header': 'first' }

> console.log(decompressor._context._table);
[ [ ':scheme', 'http', size: 43 ],
  [ ':scheme', 'https', size: 44 ],
  ...
  [ 'warning', '', size: 39 ],
  [ ':path', '/my-example/index.html', size: 59 ],
  [ 'user-agent', 'my-user-agent', size: 55 ],
  [ 'x-my-header', 'first', size: 48 ] ]

> var headerblock2 = 'a6a804261f2f6d792d6578616d706c652f7265736f75726365732f7363726970742e6a735f0a0' +
                     '67365636f6e64';

> decompressor.decompress(new Buffer(headerblock2, 'hex'));
{ 'user-agent': 'my-user-agent',
  ':path': '/my-example/resources/script.js',
  'x-my-header': 'second' }

> console.log(decompressor._context._table);
[ [ ':scheme', 'http', size: 43 ],
  [ ':scheme', 'https', size: 44 ],
  ...
  [ 'warning', '', size: 39 ],
  [ ':path', '/my-example/resources/script.js', size: 68 ],
  [ 'user-agent', 'my-user-agent', size: 55 ],
  [ 'x-my-header', 'first', size: 48 ],
  [ 'x-my-header', 'second', size: 49 ] ]

        """
        block1 = (
            '44162f6d792d6578616d706c652f696e'
            '6465782e68746d6c4d0d6d792d757365'
            '722d6167656e74400b782d6d792d6865'
            '61646572056669727374'
        ).decode("hex")
        headers1 = self.c.decode(block1)
        self.failUnless(headers1)

        block2 = (
            'a6a804261f2f6d792d6578616d706c65'
            '2f7265736f75726365732f7363726970'
            '742e6a735f0a067365636f6e64'
        ).decode("hex")

        headers2 = self.c.decode(block2)
        self.failUnless(headers2)

class TestHeaderTokeniser(unittest.TestCase):
    def setUp(self):
        self.t = self.new("")

    def new(self, *t, **k):
        from http2.protocols.http20draft4 import HeaderTokeniser
        return HeaderTokeniser(*t, **k)
        
    def test_string_literal(self):
        self.t = self.new("0161".decode("hex"))
        s = self.t.read_string()
        self.assertIsInstance(s, unicode)
        self.assertEquals(s, "a")

    def test_double_string_literal(self):
        self.t = self.new("0161 0162".replace(" ", "").decode("hex"))
        s1 = self.t.read_string()
        s2 = self.t.read_string()
        self.assertEquals(s1, "a")
        self.assertEquals(s2, "b")

    def test_bwo_byte_unprefixed_int(self):
        self.t = self.new("8800".decode("hex"))
        r = self.t.read_int()
        self.assertEqual(r, 1024)

    def test_unprefixed_int(self):
        self.t = self.new("00".decode("hex"))
        r = self.t.read_int()
        self.assertEqual(r, 0)

    def test_prefixed_int(self):
        self.t = self.new("")
        r1 = self.t.read_int(5, 129)
        r2 = self.t.read_int(5, 1)
        self.assertEqual(r1, 1)
        self.assertEqual(r2, 1)

