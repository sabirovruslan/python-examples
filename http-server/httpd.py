import logging
import mimetypes
import os
import socket
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing import Process
from urllib import parse, request

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 80
AVAILABLE_METHODS = ['GET', 'HEAD']
DEFAULT_BUFFER_SIZE = 1024


class HttpServer:

    def __init__(self, **kwargs):
        self.hostname = kwargs.get('hostname', DEFAULT_HOST)
        self.port = kwargs.get('port', DEFAULT_PORT)
        self.document_root = kwargs.get('document_root')
        self.sock = self._init_sock()

    def _init_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.hostname, self.port))
        sock.listen(1)
        logging.info('Server start')

        return sock

    def wait_for(self):
        logging.info('Start worker: {}'.format(os.getpid()))
        while True:
            sock, address = self.sock.accept()
            data = sock.recv(DEFAULT_BUFFER_SIZE)
            body = ''
            if data:
                data = data.decode('utf-8')
                method = data.split(' ')[0]
                if method not in AVAILABLE_METHODS:
                    logging.exception(f'Unknown HTTP request method: {method}')
                    response = self._create_headers(405)
                else:
                    try:
                        path_string = data.split(' ')[1]
                        path_unquoted = parse.unquote(path_string)
                        path_wo_args = path_unquoted.split('?', 1)[0]
                        if path_wo_args.endswith('/'):
                            path_wo_args += 'index.html'
                        path = os.path.join(self.document_root, *path_wo_args.split('/'))
                        if '/..' in path:
                            raise Exception('Access denied')
                        if method == 'GET':
                            with open(path, 'rb') as rd:
                                body = rd.read()
                        response = self._create_headers(200, path)
                    except Exception:
                        response = self._create_headers(404)
            else:
                response = self._create_headers(405)
            if body:
                response += body

            sock.send(response)
            sock.close()

    def _create_headers(self, code, path=''):
        h = ''
        if code == 200:
            h += 'HTTP/1.1 200 OK\r\n'
            h += 'Date: {}\r\n'.format(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
            h += 'Content-Length: {}\r\n'.format(os.path.getsize(path))
            h += 'Content-Type: {}\r\n'.format(mimetypes.guess_type(request.pathname2url(path))[0])
        elif code == 404:
            h += 'HTTP/1.1 404 Not Found\r\n'
        elif code == 405:
            h += 'HTTP/1.1 405 ERROR\r\n'

        h += 'Server: Otus-http-server\r\n'
        h += '\r\n'
        return h.encode('utf-8')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-w', help='Number of workers', default=4)
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

    process_list = []
    for _ in range(int(args.w)):
        p = Process(target=server.wait_for)
        p.daemon = True
        p.start()
        process_list.append(p)

    try:
        for p in process_list:
            p.join()
    except KeyboardInterrupt:
        for p in process_list:
            if p.is_alive():
                logging.info('Stop worker: {}'.format(p.pid))
                p.terminate()
