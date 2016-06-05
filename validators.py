# -*- coding: utf-8 -*-

import re

__author__ = 'Artem Kraynev'


def validation_email(email):
    """Валидация email"""

    reg = r'^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$'
    result = re.search(reg, email)
    if result is not None:
        is_valid = True
    else:
        is_valid = False
    return is_valid


def validation_phone(phone):
    """Валидация телефона"""

    reg = r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
    if type(phone) == int:
        phone = str(phone)
    result = re.search(reg, phone)
    if result is not None:
        is_valid = True
    else:
        is_valid = False
    return is_valid


def not_empty_test(fields):
    """Проверка на отсутствие пустых строк формы"""

    for field in fields:
        if field != '':
            not_empty = True
        else:
            not_empty = False
        return not_empty

