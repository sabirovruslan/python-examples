import logging
import mimetypes
import os
import socket
from argparse import ArgumentParser
from datetime import datetime
from urllib import parse, request

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 80
AVAILABLE_METHODS = ['GET', 'HEAD']
DEFAULT_LISTEN = 100
DEFAULT_BUFFER_SIZE = 1024


class HttpServer:

    def __init__(self, **kwargs):
        self.hostname = kwargs.get('hostname', DEFAULT_HOST)
        self.port = kwargs.get('port', DEFAULT_PORT)
        self.document_root = kwargs.get('document_root')
        self.sock = None

    def start(self):
        logging.info('Server start...')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.hostname, self.port))
        self._wait_for_connections()

    def stop(self):
        logging.info('Server stop...')
        self.sock.shutdown(socket.SHUT_RDWR)

    def _wait_for_connections(self):
        self.sock.listen(DEFAULT_LISTEN)
        sock, address = self.sock.accept()

        while True:
            data = sock.recv(DEFAULT_BUFFER_SIZE)
            body = ''
            if data:
                data = data.decode('utf-8')
                method = data.split(' ')[0]
                if method not in AVAILABLE_METHODS:
                    logging.exception(f'Unknown HTTP request method: {method}')
                    continue

                path_string = data.split(' ')[1]
                path_unquoted = parse.unquote(path_string)
                path_wo_args = path_unquoted.split('?', 1)[0]
                if path_wo_args.endswith('/'):
                    path_wo_args += 'index.html'
                path = os.path.join(self.document_root, *path_wo_args.split('/'))
                try:
                    if method == 'GET':
                        with open(path, 'rb') as rd:
                            body = rd.read().decode('utf-8')
                    headers = self._create_headers(200, path)
                except Exception as e:
                    headers = self._create_headers(404, path)
            else:
                headers = self._create_headers(405, path)
            response = headers
            if body:
                response += body

            sock.send(response.encode('utf-8'))
            sock.close()

    def _create_headers(self, code, path):
        h = ''
        if code == 200:
            h += 'HTTP/1.1 200 OK\r\n'
            h += 'Server: Otus-http-server\n'
            h += 'Date: {}\n'.format(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
            h += 'Content-Length: {}\r\n'.format(os.path.getsize(path))
            h += 'Content-Type: {}\r\n'.format(mimetypes.guess_type(request.pathname2url(path))[0])
        elif code == 404:
            h += 'HTTP/1.1 404 Not Found\r\n'
        elif code == 405:
            h += 'HTTP/1.1 405 ERROR\r\n'

        h += '\r\n'

        return h


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-w', help='Number of workers', default=100)
    parser.add_argument('-r', help='document root', default=os.path.abspath(os.path.dirname(__file__)))
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    server = HttpServer(
        hostname=os.environ.get('HOSTNAME'),
        document_root=os.path.abspath(args.r)
    )
    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
