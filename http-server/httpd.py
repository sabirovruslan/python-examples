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
    DEFAULT_BUFFER_SIZE = 10
    END_POINT = b'\r\n\r\n'

    def __init__(self, sock):
        self.sock = sock
        self.headers = []
        self.body = None

    def _read_request(self):
        result = b''
        while True:
            r = self.sock.recv(self.DEFAULT_BUFFER_SIZE)
            if not r:
                raise Exception('Connection close')
            result += r
            if self.END_POINT in result:
                return result.decode('utf-8')

    def handle_request(self):
        try:
            data = self._read_request()
        except:
            return

        try:
            method = data.split(' ')[0]
        except Exception:
            self.send_headers(NOT_ALLOWED)
            self.send_response()
            return
        if method not in self.AVAILABLE_METHODS:
            self.send_headers(BAD_REQUEST)
            self.send_response()
            return
        try:
            path_string = data.split(' ')[1]
            path = self._parse_path(path_string)
            if method == 'GET':
                with open(path, 'rb') as rd:
                    self.body = rd.read()
            self.send_headers(OK, path)
        except (FileNotFoundError, NotADirectoryError):
            self.send_headers(NOT_FOUND)
        self.send_response()

    def _parse_path(self, path_string):
        path_unquoted = parse.unquote(path_string)
        path_wo_args = path_unquoted.split('?', 1)[0]
        if path_wo_args.endswith('/'):
            path_wo_args += 'index.html'
        path = os.path.normpath(path_wo_args)
        return os.path.join(DOCUMENT_ROOT, *path.split('/'))

    def send_headers(self, code, path=''):
        if code == OK:
            self.sock.send(f'HTTP/1.1 {OK} OK\r\n'.encode('utf-8'))
            self.sock.send('Date: {}\r\n'.format(datetime.now().strftime('%d-%m-%Y %H:%M:%S')).encode('utf-8'))
            self.sock.send('Content-Length: {}\r\n'.format(os.path.getsize(path)).encode('utf-8'))
            self.sock.send('Content-Type: {}\r\n'.format(mimetypes.guess_type(request.pathname2url(path))[0]).encode('utf-8'))
        elif code == NOT_FOUND:
            self.sock.send(f'HTTP/1.1 {NOT_FOUND} Not Found\r\n'.encode('utf-8'))
        elif code == NOT_ALLOWED:
            self.sock.send(f'HTTP/1.1 {NOT_ALLOWED} ERROR\r\n'.encode('utf-8'))
        elif code == BAD_REQUEST:
            self.sock.send(f'HTTP/1.1 {BAD_REQUEST} BAD REQUEST\r\n'.encode('utf-8'))
        elif code == FORBIDDEN:
            self.sock.send(f'HTTP/1.1 {FORBIDDEN} FORBIDDEN\r\n'.encode('utf-8'))

        self.sock.send('Server: Otus-http-server\r\n'.encode('utf-8'))
        self.sock.send('\r\n'.encode('utf-8'))

    def send_response(self):
        if self.body:
            self.sock.send(self.body)
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
