
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
    def pushback(self, data):
        self.buffer = data + self.buffer
        self.has_input = True
    
    def done_sending(self):
        import socket
        self.sock.shutdown(socket.SHUT_WR)
        self.flush()

    def read(self, count, timeout=5, loop_delay=0.001):
        self.ensure_open()
        if self.buffer:
            buffer = self.buffer
            self.buffer = ''
            return buffer
        import time
        end_time = time.time() + timeout
        data = ''
        try:
            data = self._read(count)
            while not data and not self.is_closed():
                data = self._read(count)
                if data:
                    break
                if time.time() > end_time:
                    raise Timeout
                time.sleep(loop_delay)
        except EOF:
            return data
        return data

    def _read(self, count): 
        self.ensure_open()
        if not self.has_input:
            raise EOF, "No more input"
        import socket
        bytes = ''
        try:
            try:
                bytes = self.sock.recv(count)
            except socket.timeout, t:
                pass
        except IOError, ioe:
            #raise RuntimeError(dir(ioe))
            if ioe.errno in (
                socket.EBADF,
            ):
                # Closed
                self.socket_closed = True
                raise Closed, "could not read"
            else:
                raise
        if not bytes:
            # No data without an e_would_block (11) means no more data. At all.
            self.has_input = False
        return bytes
    
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
        self.has_input = False
        self.sock.close()
Stream = PushbackStream

