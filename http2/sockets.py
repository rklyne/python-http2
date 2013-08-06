
class Server(object):
    def __init__(self, host, port, stream_handler, new_socket_timeout=30):
        assert isinstance(host, str), `host`
        self.host = host
        self.port = port
        self.stream_handler = stream_handler
        self.ACCEPT_TIMEOUT = 0.1#s
        self.new_socket_timeout = new_socket_timeout
        self.running = False
        self.thread = None
    
    def start_serving(self, threaded=None, notify_serving=None):
        self.running = True
        if threaded:
            self.start_thread()
        import socket
        sock = socket.socket()
        errored = False
        try:
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.settimeout(self.ACCEPT_TIMEOUT)
                sock.bind((self.host, self.port))
                sock.listen(1)
                if notify_serving:
                    notify_serving()
            except:
                errored = True
                raise
            try:
                while self.running:
                    try:
                        child_socket, addr = sock.accept()
                    except socket.timeout:
                        pass
                    else:
                        child_socket.settimeout(self.new_socket_timeout)
                        self.dispatch(child_socket)
            except socket.error:
                pass
        finally:
            if not errored:
                try:
                    while True:
                        sock.accept()
                except (socket.timeout, socket.error):
                    pass
            sock.close()

    def start_thread(self):
        self.thread = ServerThread(self)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None

    def dispatch(self, sock):
        import http2.stream
        stream = http2.stream.PushbackStream(sock)
        try:
            if callable(self.stream_handler):
                self.stream_handler(stream)
            else:
                self.stream_handler.handle(stream)

        finally:
            # A threaded dispatcher would have to close the socket itself
            sock.close()


import threading
class ServerThread(threading.Thread):
    def __init__(self, server):
        super(ServerThread, self).__init__()
        self.server = server
    def run(self):
        self.ready_lock.acquire()
        def notify():
            self.ready_lock.release()
        self.server.start_serving(threaded=False, notify_serving=notify)
    def start(self):
        self.ready_lock = threading.Lock()
        super(ServerThread, self).start()
        self.ready_lock.acquire()
        self.ready_lock.release()
        
###
# Client code

def Stream(host, port):
    host = host
    port = port
    import socket
    sock = socket.socket()
    sock.connect((host, port))
    # TODO: Drag the socket-specific stuff out of http2.stream...
    import http2.stream
    return http2.stream.PushbackStream(sock)



