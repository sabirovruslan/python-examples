import logging
import mimetypes
import os
import socket
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing import Process
from urllib import parse, request

OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
NOT_ALLOWED = 405


class RequestHandler:
    AVAILABLE_METHODS = ['GET', 'HEAD']
    DEFAULT_BUFFER_SIZE = 1024

    def __init__(self, sock):
        self.sock = sock

    def handle_request(self):
        data = self.sock.recv(self.DEFAULT_BUFFER_SIZE)
        data = data.decode('utf-8')
        method = data.split(' ')[0]
        body = ''
        if method not in self.AVAILABLE_METHODS:
            response = self._create_headers(BAD_REQUEST)
        else:
            try:
                path_string = data.split(' ')[1]
                path = self._parse_path(path_string)
                if method == 'GET':
                    with open(path, 'rb') as rd:
                        body = rd.read()
                response = self._create_headers(OK, path)
            except (FileNotFoundError, NotADirectoryError):
                response = self._create_headers(NOT_FOUND)
        if body:
            response += body
        self.sock.send(response)
        self.sock.close()

    def _parse_path(self, path_string):
        path_unquoted = parse.unquote(path_string)
        path_wo_args = path_unquoted.split('?', 1)[0]
        path_wo_args = self._remove_dot_segments(path_wo_args)
        if path_wo_args.endswith('/'):
            path_wo_args += 'index.html'
        path = os.path.join(DOCUMENT_ROOT, *path_wo_args.split('/'))
        return path

    @staticmethod
    def _remove_dot_segments(path):
        if path.startswith('.'):
            path = '/' + path
        while '../' in path:
            p1 = path.find('/..')
            p2 = path.rfind('/', 0, p1)
            if p2 != -1:
                path = path[:p2] + path[p1 + 3:]
            else:
                path = path.replace('/..', '', 1)
        path = path.replace('/./', '/')
        path = path.replace('/.', '')
        return path

    def _create_headers(self, code, path=''):
        h = ''
        if code == OK:
            h += f'HTTP/1.1 {OK} OK\r\n'
            h += 'Date: {}\r\n'.format(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
            h += 'Content-Length: {}\r\n'.format(os.path.getsize(path))
            h += 'Content-Type: {}\r\n'.format(mimetypes.guess_type(request.pathname2url(path))[0])
        elif code == NOT_FOUND:
            h += f'HTTP/1.1 {NOT_FOUND} Not Found\r\n'
        elif code == NOT_ALLOWED:
            h += f'HTTP/1.1 {NOT_ALLOWED} ERROR\r\n'
        elif code == BAD_REQUEST:
            h += f'HTTP/1.1 {BAD_REQUEST} BAD REQUEST\r\n'
        elif code == FORBIDDEN:
            h += f'HTTP/1.1 {FORBIDDEN} FORBIDDEN\r\n'

        h += 'Server: Otus-http-server\r\n'
        h += '\r\n'
        return h.encode('utf-8')


class HttpServer:
    DEFAULT_LISTEN_BACKLOG = 10

    def __init__(self, hostname='localhost', port=80):
        self.hostname = hostname
        self.port = port
        self.sock = self._init_sock()

    def _init_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.hostname, self.port))
        sock.listen(self.DEFAULT_LISTEN_BACKLOG)
        logging.info('Server start')

        return sock

    def serve_forever(self):
        logging.info('Start worker: {}'.format(os.getpid()))
        while True:
            sock, address = self.sock.accept()
            handler = RequestHandler(sock)
            handler.handle_request()


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

    DOCUMENT_ROOT = os.path.abspath(args.r)

    server = HttpServer(
        hostname=os.environ.get('HOSTNAME'),
    )

    process_list = []
    for _ in range(int(args.w)):
        p = Process(target=server.serve_forever)
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
