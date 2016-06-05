# -*- coding: utf-8 -*-

__author__ = 'Artem Kraynev'


class RequestError(Exception):
    """Базовый класс HTTP ошибок"""
    status = 404

    def __init__(self, message, hide_traceback=False):
        super(RequestError, self).__init__(message)
        self.hide_traceback = hide_traceback


class Forbidden(RequestError):
    status = 403


class NotFound(RequestError):
    status = 404

    def __init__(self, message, hide_traceback=True):
        super(NotFound, self).__init__(message)
        self.hide_traceback = hide_traceback


class AppError(RequestError):
    status = 500

