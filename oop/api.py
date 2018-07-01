#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import re
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler

import scoring

SALT = 'Otus'
ADMIN_LOGIN = 'admin'
ADMIN_SALT = '42'
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: 'Bad Request',
    FORBIDDEN: 'Forbidden',
    NOT_FOUND: 'Not Found',
    INVALID_REQUEST: 'Invalid Request',
    INTERNAL_ERROR: 'Internal Server Error',
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: 'unknown',
    MALE: 'male',
    FEMALE: 'female',
}


class Field:
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        self.required = kwargs.get('required')
        self.nullable = kwargs.get('nullable')

    def parse(self, value):
        self.validate(value)
        return value

    def validate(self, value):
        raise NotImplementedError


class CharField(Field):
    def validate(self, value):
        if not isinstance(value, str):
            raise Exception('Field must be a string')


class ArgumentsField(Field):
    def validate(self, value):
        if not isinstance(value, dict):
            raise Exception('Field must be a dict')


class EmailField(CharField):
    __re = re.compile(r'^.+@([^.@][^@]+)$', re.IGNORECASE)

    def validate(self, value):
        match = self.__re.match(value or '')
        if not match:
            raise Exception('Not valid email')


class PhoneField(Field):
    __re = re.compile(r'(^7[\d]{10}$)')

    def validate(self, value):
        match = self.__re.match(value or '')
        if not match:
            raise Exception('Not valid phone')


class DateField(Field):

    def __init__(self, **kwargs):
        super(DateField, self).__init__(**kwargs)
        self.format = kwargs.get('format', '%d.%m.%Y')

    def validate(self, value):
        try:
            datetime.datetime.strptime(value, self.format)
        except ValueError:
            raise Exception('Field must be a date')


class BirthDayField(DateField):
    MAX_AGE = 70

    def validate(self, value):
        super(BirthDayField, self).validate(value)
        birthday = datetime.datetime.strptime(value, self.format)
        if datetime.datetime.now().year - birthday.year > self.MAX_AGE:
            raise Exception('Field must be less than 70 ages')


class GenderField(Field):
    def validate(self, value):
        if value not in GENDERS:
            raise Exception('Field must be values in list [0, 1, 2]')


class ClientIDsField(Field):
    def validate(self, value):
        if not isinstance(value, list):
            raise Exception('Field must be a list')
        if not all([isinstance(id, int) for id in value]):
            raise Exception('List values must be int')


class MetaRequest(type):
    def __new__(mcls, name, bases, attrs):
        fields = []
        for name, field in attrs.items():
            if not isinstance(field, Field):
                continue
            field.name = name
            fields.append(field)
        cls = super(MetaRequest, mcls).__new__(mcls, name, bases, attrs)
        cls.fields = fields
        return cls


class Request:
    __metaclass__ = MetaRequest

    def __init__(self, params):
        self.params = params
        self.errors = []
        self.is_cleaned = False

    def is_valid(self):
        if not self.is_cleaned:
            self.clean()
        return not self.errors

    def clean(self):
        for field in self.fields:
            value = None
            try:
                value = self.params[field.name]
            except Exception:
                self.errors.append(f'Field "{field.name}" not found')
                continue
            if not value and value != 0:
                if field.nullable:
                    setattr(self, field.name, value)
                else:
                    self.errors.append(f'Field "{field.name}" not nullable')
                continue
            try:
                setattr(self, field.name, field.parse(value))
            except Exception as e:
                self.errors.append(f'Field "{field.name}" error {e}')
        self.is_cleaned = True

    def get_error_to_string(self):
        return ', '.join(self.errors)


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def is_valid(self):
        if not super(OnlineScoreRequest, self).is_valid():
            return False

    def _check_fields(self):
        return not (self.phone and self.email) and not (self.first_name and self.last_name) \
               and not bool(self.gender is not None and self.birthday)


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class RequestHandler:
    def validate_handle(self, request, arguments, ctx):
        if arguments.is_valid():
            return arguments.get_error_to_string, INVALID_REQUEST
        return self.handle(request, arguments, ctx, None)

    def handle(self, request, arguments, ctx, store):
        return {}, OK


class ClientsInterestsHandler(RequestHandler):
    type = ClientsInterestsRequest

    def handle(self, request, arguments, ctx, store):
        ctx['nclients'] = len(arguments.client_ids)
        return {cid: scoring.get_interests(store, cid) for cid in arguments.client_ids}, OK


class OnlineScoreHandler(RequestHandler):
    type = OnlineScoreRequest

    def handle(self, request, arguments, ctx, store):
        score = 42
        if not request.is_admin:
            score = scoring.get_score(store, **arguments)
        ctx['has'] = [field.name for field in self.type.fields if getattr(arguments, field.name)]
        return {'score': score}, OK


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime('%Y%m%d%H') + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    handlers = {
        'clients_interests': lambda: ClientsInterestsHandler(),
        'online_score': lambda: OnlineScoreHandler()
    }
    method_request = MethodRequest(request['body'])
    if not method_request.is_valid():
        return method_request.get_error_to_string(), INVALID_REQUEST
    if not check_auth(method_request):
        return None, FORBIDDEN
    handler = handlers.get(method_request.method)
    if not handler:
        return "Method not found", NOT_FOUND
    return handler.validate_handle(method_request, handler.type(method_request.arguments), ctx, store)


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        'method': method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {'request_id': self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip('/')
            logging.info('%s: %s %s' % (self.path, data_string, context['request_id']))
            if path in self.router:
                try:
                    response, code = self.router[path]({'body': request, 'headers': self.headers}, context, self.store)
                except Exception as e:
                    logging.exception('Unexpected error: %s' % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if code not in ERRORS:
            r = {'response': response, 'code': code}
        else:
            r = {'error': response or ERRORS.get(code, 'Unknown Error'), 'code': code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == '__main__':
    op = OptionParser()
    op.add_option('-p', '--port', action='store', type=int, default=8080)
    op.add_option('-l', '--log', action='store', default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(('localhost', opts.port), MainHTTPHandler)
    logging.info('Starting server at %s' % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
