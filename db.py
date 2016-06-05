# -*- coding: utf-8 -*-

from psycopg2 import connect, extras

__author__ = 'Artem Kraynev'


def select_all(db_name):
    """Запрос ВСЕХ данных с произвольной таблицы"""
    # УКАЖИТЕ СВОЕГО ПОЛЬЗОВАТЕЛЯ И СВОЙ ПАРОЛЬ
    conn = connect("dbname='comment_form' user='postgres' host='localhost' password='123'")
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    cur.execute("SELECT * FROM %s;" % (db_name,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def select_filter_all(row_name, row_val, db_name):
    """Запрос данных с произвольной таблицы с указанной строки"""
    # УКАЖИТЕ СВОЕГО ПОЛЬЗОВАТЕЛЯ И СВОЙ ПАРОЛЬ
    conn = connect("dbname='comment_form' user='postgres' host='localhost' password='123'")
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    cur.execute("SELECT * FROM %s  WHERE %s = %s;" % (db_name, row_name, row_val))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def select_filter(req_row, row_name, row_val, db_name):
    """Запрос значения колонки с произвольной таблицы с указанной строки"""
    # УКАЖИТЕ СВОЕГО ПОЛЬЗОВАТЕЛЯ И СВОЙ ПАРОЛЬ
    conn = connect("dbname='comment_form' user='postgres' host='localhost' password='123'")
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    cur.execute("SELECT %s FROM %s  WHERE %s = '%s';" % (req_row, db_name, row_name, row_val))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def insert_comment_tb(date, surname, name, middle_name, region, city, phone, email, comment):
    """Запись данный в таблицу comment"""
    # УКАЖИТЕ СВОЕГО ПОЛЬЗОВАТЕЛЯ И СВОЙ ПАРОЛЬ
    conn = connect("dbname='comment_form' user='postgres' host='localhost' password='123'")
    cur = conn.cursor()
    cur.execute("""INSERT INTO comment
                (date, surname, name, middle_name, region, city, phone, email, comment)
                VALUES ('%s','%s', '%s', '%s', '%s', '%s', %s, '%s', '%s');""" %
                (date, surname, name, middle_name, region, city, phone, email, comment))
    cur.close()
    conn.close()


def delete_row(row_name, row_val, db_name):
    """Удаление данных с произвольной таблицы с указанной строки"""
    # УКАЖИТЕ СВОЕГО ПОЛЬЗОВАТЕЛЯ И СВОЙ ПАРОЛЬ
    conn = connect("dbname='comment_form' user='postgres' host='localhost' password='123'")
    cur = conn.cursor()
    cur.execute("DELETE FROM %s  WHERE %s = %s;" % (db_name, row_name, row_val))
    conn.commit()
    cur.close()
    conn.close()


def update_tb(db_name, id_val):
    """Накручивает счетчик комментариев"""
    # УКАЖИТЕ СВОЕГО ПОЛЬЗОВАТЕЛЯ И СВОЙ ПАРОЛЬ
    conn = connect("dbname='comment_form' user='postgres' host='localhost' password='123'")
    cur = conn.cursor()
    cur.execute("UPDATE %s SET quantity_comments=quantity_comments+1 WHERE id=%s" % (db_name, id_val))
    conn.commit()
    cur.close()
    conn.close()


def update_comment_col(id_val):
    """Обнуляет колонку comment на определеной строке таблицы"""
    # УКАЖИТЕ СВОЕГО ПОЛЬЗОВАТЕЛЯ И СВОЙ ПАРОЛЬ
    conn = connect("dbname='comment_form' user='postgres' host='localhost' password='123'")
    cur = conn.cursor()
    cur.execute("UPDATE comment SET comment = NULL WHERE id=%s" % (id_val,))
    conn.commit()
    cur.close()
    conn.close()


def get_json_from_db():
    """
    Преобразования данных с таблиц
    city и region в обьект типа JSON
    """

    query_region = select_all(db_name='region')
    query_city = select_all(db_name='city')
    json_dict = {
        'region': {
            '1': query_region[0][1],
            '2': query_region[1][1],
            '3': query_region[2][1]
        },
        'city': {
            '1': [
                query_city[0][2],
                query_city[1][2],
                query_city[2][2]
            ],
            '2': [
                query_city[3][2],
                query_city[4][2],
                query_city[5][2]
            ],
            '3': [
                query_city[6][2],
                query_city[7][2],
                query_city[8][2]
            ],
        }
    }
    return json_dict






