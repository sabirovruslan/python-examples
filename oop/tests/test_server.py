import datetime
import hashlib
import json
import os
import socket
from http.server import HTTPServer
from threading import Thread
from unittest import TestCase

import requests

import api
from store import Store, MemcacheAdapter
from tests.utils import cases


class MainHandlerTest(TestCase):

    def setUp(self):
        self.port = self.get_port()
        self.handler_url = f'http://localhost:{self.port}/method/'
        self.server = HTTPServer(('localhost', self.port), api.MainHTTPHandler)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.setDaemon(True)
        self.server_thread.start()
        self.store = Store(MemcacheAdapter(
            address=os.environ['STORE_PORT_11211_TCP_ADDR'],
            port=os.environ['STORE_PORT_11211_TCP_PORT']
        ))

    def set_valid_auth(self, request):
        if request.get('login') == api.ADMIN_LOGIN:
            msg = (datetime.datetime.now().strftime('%Y%m%d%H') + api.ADMIN_SALT).encode('utf-8')
            request['token'] = hashlib.sha512(msg).hexdigest()
        else:
            msg = (request.get('account', '') + request.get('login', '') + api.SALT).encode('utf-8')
            request['token'] = hashlib.sha512(msg).hexdigest()

    @staticmethod
    def get_port():
        soct = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        soct.bind(('localhost', 0))
        address, port = soct.getsockname()
        soct.close()
        return port

    def test_check(self):
        self.assertEqual(1, 1)

    @cases([
        {
            'account': 'account_test',
            'login': 'login',
            'method': 'online_score',
            'token': '',
            'arguments': {
                'phone': '79175002040',
                'email': 'stupnikov@otus.ru',
                'first_name': 'Test',
                'last_name': 'Testovich',
                'birthday': '01.01.2000',
                'gender': 1
            }
        }
    ])
    def test_score_request(self, request):
        self.set_valid_auth(request)
        response = requests.post(self.handler_url, json=request)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.json()['response']['score'], 5.0)

    @cases([
        {
            'account': 'account_test',
            'login': 'login',
            'method': 'clients_interests',
            'token': '',
            'arguments': {
                'client_ids': [1, 2, 3, 4],
                'date': '01.01.2000'
            }
        }
    ])
    def test_client_interests(self, request):
        self.set_valid_auth(request)

        score_data = {
            "1": {'i': ["travel", "geek"]},
            "2": {'i': ["sport", "cars"]},
            "3": {'i': ["books", "sport"]},
            "4": {'i': ["hi-tech", "cinema"]}
        }

        self.store.cache_set('i:1', json.dumps(score_data.get('1')).encode('utf-8'), 10)
        self.store.cache_set('i:2', json.dumps(score_data.get('2')).encode('utf-8'), 10)
        self.store.cache_set('i:3', json.dumps(score_data.get('3')).encode('utf-8'), 10)
        self.store.cache_set('i:4', json.dumps(score_data.get('4')).encode('utf-8'), 10)

        response = requests.post(self.handler_url, json=request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['response'], score_data)

    @cases([
        {
            'account': 'account_test',
            'login': 'login',
            'method': '404_method',
            'token': '',
            'arguments': {}
        }
    ])
    def test_method_not_found(self, request):
        self.set_valid_auth(request)
        response = requests.post(self.handler_url, json=request)
        self.assertEqual(response.status_code, 404)

    @cases([
        {
            'account': 'account_test',
            'login': 'login',
            'method': 'clients_interests',
            'token': '',
            'arguments': {}
        }
    ])
    def test_method_forbidden(self, request):
        response = requests.post(self.handler_url, json=request)
        self.assertEqual(response.status_code, 403)

    def test_method_bad_request(self):
        response = requests.post(self.handler_url)
        self.assertEqual(response.status_code, 400)

    @cases([
        {
            'account': 'account_test',
            'login': 'login',
            'method': 'online_score',
            'token': '',
            'arguments': {
                'phone': '79175002040',
                'email': 'stupnikov@otus.ru',
                'first_name': 'Test',
                'last_name': 'Testovich',
                'birthday': '01.01.2000',
                'gender': '4'
            }
        },
        {
            'account': 'account_test',
            'login': 'login',
            'method': 'online_score',
            'token': '',
            'arguments': {
                'phone': '89175002040',
                'email': 'stupn@ikov@otus.ru',
                'first_name': 'Test',
                'last_name': 'Testovich',
                'birthday': '01.01.2000',
                'gender': 1
            }
        }
    ])
    def test_score_request_invalid_request(self, request):
        self.set_valid_auth(request)
        response = requests.post(self.handler_url, json=request)
        self.assertEqual(response.status_code, 422)
