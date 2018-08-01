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
    RECV_STEP_SIZE = 10
    DELIMETER = b'\r\n\r\n'

    def __init__(self, sock):
        self.sock = sock
        self.headers = []
        self.body = ''

    def _read_request(self):
        buffer = b''
        result_size = 0
        while len(buffer) >= result_size:
            r = self.sock.recv(self.RECV_STEP_SIZE)
            if not r:
                raise Exception('Connection close')
            buffer += r
            if self.DELIMETER in buffer:
                break
            result_size += self.RECV_STEP_SIZE
        return buffer.decode('utf-8')

    def handle_request(self):
        try:
            data = self._read_request()
        except:
            return

        try:
            method = data.split(' ')[0]
        except Exception:
            self.create_headers(BAD_REQUEST)
            self.send_response()
            return
        if method not in self.AVAILABLE_METHODS:
            self.create_headers(NOT_ALLOWED)
            self.send_response()
            return
        try:
            path_string = data.split(' ')[1]
            path = self._parse_path(path_string)
            if method == 'GET':
                with open(path, 'rb') as rd:
                    self.body = rd.read()
            self.create_headers(OK, path)
        except (FileNotFoundError, NotADirectoryError):
            self.create_headers(NOT_FOUND)
        self.send_response()

    def _parse_path(self, path_string):
        path_unquoted = parse.unquote(path_string)
        path_wo_args = path_unquoted.split('?', 1)[0]
        if path_wo_args.endswith('/'):
            path_wo_args += 'index.html'
        path = os.path.normpath(path_wo_args)
        return os.path.join(DOCUMENT_ROOT, *path.split('/'))

    def create_headers(self, code, path=''):
        if code == OK:
            self.headers.append(f'HTTP/1.1 {OK} OK\r\n')
            self.headers.append('Date: {}\r\n'.format(datetime.now().strftime('%d-%m-%Y %H:%M:%S')))
            self.headers.append('Content-Length: {}\r\n'.format(os.path.getsize(path)))
            self.headers.append('Content-Type: {}\r\n'.format(mimetypes.guess_type(request.pathname2url(path))[0]))
        elif code == NOT_FOUND:
            self.headers.append(f'HTTP/1.1 {NOT_FOUND} Not Found\r\n')
        elif code == NOT_ALLOWED:
            self.headers.append(f'HTTP/1.1 {NOT_ALLOWED} ERROR\r\n')
        elif code == BAD_REQUEST:
            self.headers.append(f'HTTP/1.1 {BAD_REQUEST} BAD REQUEST\r\n')
        elif code == FORBIDDEN:
            self.headers.append(f'HTTP/1.1 {FORBIDDEN} FORBIDDEN\r\n')

        self.headers.append('Server: Otus-http-server\r\n')
        self.headers.append('\r\n')

    def send_response(self):
        response = ''.join(self.headers).encode('utf-8')
        if self.body:
            response += self.body
        self.sock.sendall(response)
        self.sock.close()


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
