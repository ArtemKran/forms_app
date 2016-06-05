# -*- coding: utf-8 -*-

__author__ = 'Artem Kraynev'


class LazyProperty(object):
    """Свойство, значение которого вычисляется только один раз"""
    def __init__(self, function):
        self._function = function

    def __get__(self, obj, _=None):
        if obj is None:
            return self

        value = self._function(obj)
        setattr(obj, self._function.func_name, value)
        return value
