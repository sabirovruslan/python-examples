import os
import socket

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 80


class HttpServer:

    def __init__(self, hostname=DEFAULT_HOST, port=DEFAULT_PORT):
        self.hostname = hostname
        self.port = port
        self.document_root = ''
        self.sock = None

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.hostname, self.port))
        self._wait_for_connections()

    def _wait_for_connections(self):
        self.sock.listen(100)
        sock, address = self.sock.accept()

        while True:
            data = sock.recv(1024)
            if not data:
                break
            sock.send(data)
        sock.close()


if __name__ == '__main__':
    server = HttpServer(hostname=os.environ.get('HOSTNAME'))
    server.start()
