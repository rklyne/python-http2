
class Timeout(Exception): pass
class Error(Exception): pass
class Closed(Error): pass
class EOF(Error): pass

class PushbackStream(object):
    USE_FILE = False
    def __init__(self, socket):
        self.sock = socket
        socket.setblocking(0)
        socket.settimeout(0.1)
        if self.USE_FILE:
            self.file = socket.makefile('wb')
        self.socket_closed = False
        self.buffer = ''
        self.has_input = True
        self.stream_finished = False
    def pushback(self, data):
        self.buffer = data + self.buffer
        self.has_input = True
    
    def done_sending(self):
        import socket
        self.sock.shutdown(socket.SHUT_WR)
        self.flush()

    def read(self, count, timeout=5, loop_delay=0.001):
        import socket
        self.ensure_open()
        import time
        end_time = time.time() + timeout
        import cStringIO as StringIO
        data = StringIO.StringIO()
        if self.buffer:
            data.write(self.buffer)
            self.buffer = ''
        if not self.stream_finished:
            try:
                while data.tell() < count and not self.is_closed() and not self.stream_finished:
                    try:
                        assert not self.stream_finished
                        bytes = self.sock.recv(count)
                        if not bytes:
                            self.has_input = False
                            self.stream_finished = True
                            break
                    except socket.timeout, t:
                        pass
                    else:
                        data.write(bytes)
                        if time.time() > end_time:
                            raise Timeout
                        time.sleep(loop_delay)
            except EOF:
                raise
                pass
        all_data = data.getvalue()
        requested_data, extra_data = all_data[:count], all_data[count:]
        self.pushback(extra_data)
        if self.stream_finished and not self.buffer:
            self.has_input = False
        return requested_data

    def flush(self):
        if not self.USE_FILE:
            # Sockets aren't very flushable
            return
        self.file.flush()

    def write(self, bytes):
        self.ensure_open()
        import socket
        try:
            self.sock.sendall(bytes)
        except socket.error, ioe:
            if ioe.errno == socket.EBADF:
                self.socket_closed = True
                raise Closed, "Could not send %r" % bytes
            else:
                raise

    def ensure_open(self):
        if self.is_closed():
            raise Closed

    def is_closed(self):
        return self.socket_closed

    def close(self):
        self.socket_closed = True
        self.stream_finished = True
#        self.has_input = False
        self.sock.close()
Stream = PushbackStream

