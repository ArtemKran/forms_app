# -*- coding: utf-8 -*-

import cgi
import mimetypes
import os
import re
import StringIO
import sys
import traceback
from urlparse import parse_qs
from wsgiref.simple_server import make_server
from errors import RequestError, Forbidden, NotFound
from decorators import LazyProperty

__author__ = 'Artem Kraynev'

# HTTP методы
REQUEST_MAPPINGS = {
    'GET': [],
    'POST': [],
}

ERROR_HANDLERS = {}

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

# Словарь кодов HTTP ответа
# Возможно перечислить все виды кодов,
# написаны лишь возможно встречаемые
# в данном предложении
HTTP_MAPPINGS = {
    200: 'OK',
    201: 'CREATED',
    202: 'ACCEPTED',
    204: 'NO CONTENT',
    205: 'RESET CONTENT',
    302: 'FOUND',
    400: 'BAD REQUEST',
    403: 'FORBIDDEN',
    404: 'NOT FOUND',
    500: 'INTERNAL SERVER ERROR',
    501: 'NOT IMPLEMENTED',
}


class HTTPHeaders(dict):
    """Парсинг HTTP заголовков"""

    def __init__(self, *args, **kwargs):
        super(HTTPHeaders, self).__init__()
        self._as_list = {}
        self._last_key = None
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], HTTPHeaders):
            for k, v in args[0].get_all():
                self.add(k, v)
        else:
            self.update(*args, **kwargs)

    def add(self, name, value):
        norm_name = HTTPHeaders._normalize_name(name)
        self._last_key = norm_name
        if norm_name in self:
            dict.__setitem__(self, norm_name, self[norm_name] + ',' + value)
            self._as_list[norm_name].append(value)
        else:
            self[norm_name] = value

    def get_list(self, name):
        norm_name = HTTPHeaders._normalize_name(name)
        return self._as_list.get(norm_name, [])

    def get_all(self):
        for name, list in self._as_list.items():
            for value in list:
                yield (name, value)

    def parse_line(self, line):
        if line[0].isspace():
            new_part = ' ' + line.lstrip()
            self._as_list[self._last_key][-1] += new_part
            dict.__setitem__(self, self._last_key, self[self._last_key] + new_part)
        else:
            name, value = line.split(":", 1)
            self.add(name, value.strip())

    @classmethod
    def parse(cls, headers):
        """Возвращает словарь из заголовка HTTP
        """
        h = cls()
        for line in headers.splitlines():
            if line:
                h.parse_line(line)
        return h

    def __setitem__(self, name, value):
        norm_name = HTTPHeaders._normalize_name(name)
        dict.__setitem__(self, norm_name, value)
        self._as_list[norm_name] = [value]

    def __getitem__(self, name):
        return dict.__getitem__(self, HTTPHeaders._normalize_name(name))

    def __delitem__(self, name):
        norm_name = HTTPHeaders._normalize_name(name)
        dict.__delitem__(self, norm_name)
        del self._as_list[norm_name]

    def __contains__(self, name):
        norm_name = HTTPHeaders._normalize_name(name)
        return dict.__contains__(self, norm_name)

    def get(self, name, default=None):
        return dict.get(self, HTTPHeaders._normalize_name(name), default)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def copy(self):
        return HTTPHeaders(self)

    _NORMALIZED_HEADER_RE = re.compile(
        r'^[A-Z0-9][a-z0-9]*(-[A-Z0-9][a-z0-9]*)*$'
    )
    _normalized_headers = {}

    @staticmethod
    def _normalize_name(name):
        try:
            return HTTPHeaders._normalized_headers[name]
        except KeyError:
            if HTTPHeaders._NORMALIZED_HEADER_RE.match(name):
                normalized = name
            else:
                normalized = "-".join(
                    [w.capitalize() for w in name.split("-")])
            HTTPHeaders._normalized_headers[name] = normalized
            return normalized


class Request(object):
    """Класс для HTTP request"""
    GET = {}

    def __init__(self, environ, start_response):
        self._environ = environ
        self._start_response = start_response
        self.path = add_slash(self._environ.get('PATH_INFO', ''))
        self.method = self._environ.get('REQUEST_METHOD', 'GET').upper()
        self.query = self._environ.get('QUERY_STRING', '')
        self.content_length = 0
        self.headers = HTTPHeaders()
        if self._environ.get("CONTENT_TYPE"):
            self.headers["Content-Type"] = self._environ["CONTENT_TYPE"]
        if self._environ.get("CONTENT_LENGTH"):
            self.headers["Content-Length"] = self._environ["CONTENT_LENGTH"]
        for key in self._environ:
            if key.startswith("HTTP_"):
                self.headers[key[5:].replace("_", "-")] = self._environ[key]
        try:
            self.content_length = int(self._environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            pass

        self.GET = self.build_get_dict()

    def __getattr__(self, name):
        return self._environ[name]

    @LazyProperty
    def POST(self):
        return self.build_post_dict()

    @LazyProperty
    def body(self):
        """Содержимое request"""
        return self._environ['wsgi.input'].read(self.content_length)

    def build_get_dict(self):
        """Берет данные с GET запроса и кладет их в словарь"""
        raw_query_dict = parse_qs(self.query, keep_blank_values=1)
        query_dict = {}

        for key, value in raw_query_dict.items():
            if len(value) <= 1:
                query_dict[key] = value[0]
            else:
                query_dict[key] = value

        return query_dict

    def build_post_dict(self):
        """Берет данные с POST запроса и кладет их в словарь"""
        # Так же может использоваться для PUT запроса

        raw_data = cgi.FieldStorage(fp=StringIO.StringIO(self.body), environ=self._environ)
        query_dict = {}

        for field in raw_data:
            if isinstance(raw_data[field], list):
                query_dict[field] = [fs.value for fs in raw_data[field]]
            elif raw_data[field].filename:
                query_dict[field] = raw_data[field]
            else:
                query_dict[field] = raw_data[field].value

        return query_dict


class Response(object):
    """Класс для HTTP response"""

    def __init__(self, output, headers=None, status=200, content_type='text/html'):
        self.output = output
        self.content_type = content_type
        self.status = status
        self.headers = HTTPHeaders()

        if headers and isinstance(headers, HTTPHeaders):
            self.headers = headers
        if headers and isinstance(headers, list):
            for (key, value) in headers:
                self.headers.add(key, value)

    def add_header(self, key, value):
        self.headers.add(key, value)

    def send(self, start_response):
        status = "%d %s" % (self.status, HTTP_MAPPINGS.get(self.status))
        headers = ([('Content-Type', "%s; charset=utf-8" % self.content_type)] +
                   [(k, v) for k, v in self.headers.iteritems()])

        start_response(status, headers)

        if isinstance(self.output, unicode):
            return self.output.encode('utf-8')
        else:
            return self.output


def handle_request(environ, start_response):
    """Главный обработчик"""
    try:
        request = Request(environ, start_response)
    except Exception, e:
        return handle_error(e)

    try:
        (re_url, url, callback), kwargs = find_matching_url(request)
        response = callback(request, **kwargs)
    except Exception, e:
        return handle_error(e, request)

    if not isinstance(response, Response):
        response = Response(response)

    return response.send(start_response)


def handle_error(exception, request=None):
    """При исключении выводит на страницу ошибки"""
    if request is None:
        request = {'_environ': {'PATH_INFO': ''}}

    if not getattr(exception, 'hide_traceback', False):
        (e_type, e_value, e_tb) = sys.exc_info()
        message = "%s occurred on '%s': %s\nTraceback: %s" % (
            exception.__class__,
            request._environ['PATH_INFO'],
            exception,
            ''.join(traceback.format_exception(e_type, e_value, e_tb))
        )
        request._environ['wsgi.errors'].write(message)

    if isinstance(exception, RequestError):
        status = getattr(exception, 'status', 404)
    else:
        status = 500

    if status in ERROR_HANDLERS:
        return ERROR_HANDLERS[status](request, exception)

    return not_found(request, exception)


def find_matching_url(request):
    """
    Определяет есть ли метод запроса в REQUEST_MAPPINGS
    """
    if request.method not in REQUEST_MAPPINGS:
        raise NotFound("The HTTP request method '%s' is not supported." % request.method)

    for url_set in REQUEST_MAPPINGS[request.method]:
        match = url_set[0].search(request.path)

        if match is not None:
            return url_set, match.groupdict()

    raise NotFound("Sorry, nothing here.")


# МЕДИА ФАЙЛЫ


def content_type(filename):
    """
    Определяет какой мими-тип у загружаемого файла
    """
    ct = 'text/plain'
    ct_guess = mimetypes.guess_type(filename)

    if ct_guess[0] is not None:
        ct = ct_guess[0]

    return ct


def static_file(filename, root=MEDIA_ROOT):
    """
    Выдает статический файл из файловой системы,
    указанной в MEDIA_ROOT.
    """
    if filename is None:
        raise Forbidden("You must specify a file you'd like to access.")

    valid_path = filename.strip('/')

    valid_path = valid_path.replace('//', '/').replace('/./', '/').replace('/../', '/')

    desired_path = os.path.join(root, valid_path)

    if not os.path.exists(desired_path):
        raise NotFound("File does not exist.")

    if not os.access(desired_path, os.R_OK):
        raise Forbidden("You do not have permission to access this file.")

    ct = str(content_type(desired_path))

    if ct.startswith('text') or ct.endswith('xml') or ct.endswith('json'):
        return open(desired_path, 'r').read()

    return open(desired_path, 'rb').read()


def serve_static_file(request, filename, root=MEDIA_ROOT, force_content_type=None):
    """
    Базовый обработчик для поиска медиа файлов
    """
    file_contents = static_file(filename, root)

    if force_content_type is None:
        ct = content_type(filename)
    else:
        ct = force_content_type

    return Response(file_contents, content_type=ct)


def add_slash(url):
    """Добавляет слэш к URL"""
    if not url.endswith('/'):
        url += '/'
    return url


# Декораторы для запросов GET и POST,
# таким же макаром можно написать
# декораторы для PUT и DELETE

def get(url):
    """Декоратор для GET запроса"""
    def wrapped(method):
        re_url = re.compile("^%s$" % add_slash(url))
        REQUEST_MAPPINGS['GET'].append((re_url, url, method))
        return method
    return wrapped


def post(url):
    """Декоратор для POST запроса"""
    def wrapped(method):
        re_url = re.compile("^%s$" % add_slash(url))
        REQUEST_MAPPINGS['POST'].append((re_url, url, method))
        return method
    return wrapped


def error(code):
    """Декоратор для обработки HTTP ошибок"""
    def wrapped(method):
        ERROR_HANDLERS[code] = method
        return method
    return wrapped


# Обработчики ошибок HTTP

@error(403)
def forbidden(request, exception):
    response = Response('Forbidden', status=403, content_type='text/plain')
    return response.send(request._start_response)


@error(404)
def not_found(request, exception):
    response = Response('Not Found', status=404, content_type='text/plain')
    return response.send(request._start_response)


@error(500)
def app_error(request, exception):
    response = Response('Application Error', status=500, content_type='text/plain')
    return response.send(request._start_response)


@error(302)
def redirect(request, exception):
    response = Response('', status=302, content_type='text/plain', headers=[('Location', exception.url)])
    return response.send(request._start_response)


# Запуск сервера

def run_app():
    srv = make_server('', 8000, handle_request)
    print "Serving on port 8000..."
    srv.serve_forever()

