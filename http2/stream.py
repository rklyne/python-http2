

class PushbackStream(object):
    USE_FILE = False
    def __init__(self, socket):
        self.sock = socket
        socket.setblocking(0)
        socket.settimeout(1)
        if self.USE_FILE:
            self.file = socket.makefile('wb')
        self.socket_closed = False
        self.buffer = ''
    def pushback(self, data):
        self.buffer = data + self.buffer
    
    def done_sending(self):
        import socket
        self.sock.shutdown(socket.SHUT_WR)
        self.flush()

    def read(self, count, timeout=5, loop_delay=0.01):
        if self.buffer:
            buffer = self.buffer
            self.buffer = ''
            return buffer
        import time
        end_time = time.time() + timeout
        data = self._read(count)
        while not data:
            data = self._read(count)
            if data:
                break
            if time.time() > end_time:
                return ""
            time.sleep(loop_delay)
        return data

    def _read(self, count): 
        import socket
        try:
            while True:
                try:
                    bytes = self.sock.recv(count)
                    break
                except socket.timeout, t:
                    pass
        except IOError, ioe:
            #raise RuntimeError(dir(ioe))
            if ioe.errno == 11:
                return ""
            raise
        if not bytes:
            self.socket_closed = True
        return bytes
    
    def flush(self):
        if not self.USE_FILE:
            # Sockets aren't very flushable
            return
        self.file.flush()

    def write(self, bytes):
        self.sock.sendall(bytes)

    def is_closed(self):
        return self.socket_closed

