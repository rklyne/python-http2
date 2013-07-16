import unittest

class TestFrameWithPayload(unittest.TestCase):
    def get_frame_bytes(self):
        # An empty settings frame
        return """
        00 01 04 00 00 00 00 00 61
        """.replace(" ", "").replace("\n", "").decode("hex")
    
    def test_write_frame(self):
        import http2.protocols.http20draft4 as http20
        frame = http20.Frame(http20.FRAME_SETTINGS, 0, 0, 'a')
        self.assertEqual(frame.as_bytes(), self.get_frame_bytes())

    def test_read_frame(self):
        import http2.protocols.http20draft4 as http20
        frame = http20.Frame.from_bytes(self.get_frame_bytes())
        self.failUnless(frame)
        self.assertEqual(frame.type_id, http20.FRAME_SETTINGS)
        self.assertEqual(frame.payload, 'a')
        self.assertEqual(frame.flags, 0)
        self.assertEqual(frame.stream_id, 0)


class TestFrameWithoutPayload(unittest.TestCase):
    def get_frame_bytes(self):
        # An empty settings frame
        return """
        00 00 04 00 00 00 00 00
        """.replace(" ", "").replace("\n", "").decode("hex")
    
    def test_write_frame(self):
        import http2.protocols.http20draft4 as http20
        frame = http20.Frame(http20.FRAME_SETTINGS, 0, 0, '')
        self.assertEqual(frame.as_bytes(), self.get_frame_bytes())

    def test_read_frame(self):
        import http2.protocols.http20draft4 as http20
        frame = http20.Frame.from_bytes(self.get_frame_bytes())
        self.failUnless(frame)
        self.assertEqual(frame.type_id, http20.FRAME_SETTINGS)
        self.assertEqual(frame.payload, '')
        self.assertEqual(frame.flags, 0)
        self.assertEqual(frame.stream_id, 0)


