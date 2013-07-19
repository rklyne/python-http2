class Http2Exception(Exception):
    num = None
    def __init__(self):
        assert self.num is not None

"""
"""
class Success(Http2Exception):
    """
NO_ERROR (0):  The associated condition is not as a result of an error.  For example, a GOAWAY might include this code to indicate graceful shutdown of a connection.
"""
    num = 0


class ProtocolError(Http2Exception):
    """
PROTOCOL_ERROR (1):  The endpoint detected an unspecific protocol error.  This error is for use when a more specific error code is not available.
    """
    num = 1

class InternalError(Http2Exception):
    """
INTERNAL_ERROR (2):  The endpoint encountered an unexpected internal error.
    """
    num = 2

class FlowControlError(Http2Exception):
    """
FLOW_CONTROL_ERROR (3):  The endpoint detected that its peer violated the flow control protocol.
    """
    num = 3

class StreamClosed(Http2Exception):
    """
STREAM_CLOSED (5):  The endpoint received a frame after a stream was half closed.
    """
    num = 5

class FrameTooLarge(Http2Exception):
    """
FRAME_TOO_LARGE (6):  The endpoint received a frame that was larger than the maximum size that it supports.
    """
    num = 6

class RefusedStream(Http2Exception):
    """
REFUSED_STREAM (7):  The endpoint refuses the stream prior to performing any application processing, see Section 8.1.5 for details.
    """
    num = 7

class Cancel(Http2Exception):
    """
CANCEL (8):  Used by the endpoint to indicate that the stream is no longer needed.
    """
    num = 8

class CompressionError(Http2Exception):
    """
COMPRESSION_ERROR (9):  The endpoint is unable to maintain the compression context for the connection.
    """
    num = 9


