# -*- coding: utf-8 -*-

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

__author__ = 'Artem Kraynev'


def create_db():
    """Создает базу данных"""
    # УКАЖИТЕ СВОЕГО ПОЛЬЗОВАТЕЛЯ И СВОЙ ПАРОЛЬ
    conn = connect("dbname='postgres' user='postgres' host='localhost' password='123'")
    dbname = "comment_form"
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("CREATE DATABASE %s" % dbname)
    cur.close()
    conn.close()


def create_tbs():
    """Создает таблицы comment, region и city"""
    # УКАЖИТЕ СВОЕГО ПОЛЬЗОВАТЕЛЯ И СВОЙ ПАРОЛЬ
    conn = connect("dbname='comment_form' user='postgres' host='localhost' password='123'")
    cur = conn.cursor()

    # Конечно же поле date нужно создавать типа
    # timestamp without(with) time zone...
    cur.execute("""CREATE SEQUENCE comment_seq;
                CREATE TABLE comment (
                id int PRIMARY KEY default nextval('comment_seq'),
                surname varchar(30),
                name varchar(30),
                middle_name varchar(30),
                region varchar(50),
                city varchar(30),
                email varchar(30),
                comment varchar(200),
                phone varchar(15),
                date varchar(30));""")

    cur.execute("""CREATE SEQUENCE region_seq;
                CREATE TABLE region (
                id int PRIMARY KEY default nextval('region_seq'),
                region varchar(30),
                quantity_comments integer);""")

    cur.execute("""CREATE SEQUENCE city_seq;
                CREATE TABLE city (
                id int PRIMARY KEY default nextval('city_seq'),
                region_id int references region(id),
                city varchar(30),
                quantity_comments integer);""")

    conn.commit()
    cur.close()
    conn.close()


def insert_tbs():
    """
    Запись в таблицы region и city первоначальных данных,
    необходимых для работы формы
    """
    # УКАЖИТЕ СВОЕГО ПОЛЬЗОВАТЕЛЯ И СВОЙ ПАРОЛЬ
    conn = connect("dbname='comment_form' user='postgres' host='localhost' password='123'")
    cur = conn.cursor()
    cur.execute("""INSERT INTO region (region) VALUES
                ('Краснодарский край'),
                ('Ростовская область'),
                ('Ставропольский край');""")

    cur.execute("""INSERT INTO city (region_id, city) VALUES
                (1, 'Краснодар'),
                (1, 'Кропоткин'),
                (1, 'Славянск');""")

    cur.execute("""INSERT INTO city (region_id, city) VALUES
                (2, 'Ростов'),
                (2, 'Шахты'),
                (2, 'Батайск');""")

    cur.execute("""INSERT INTO city (region_id, city) VALUES
                (3, 'Ставрополь'),
                (3, 'Пятигорск'),
                (3, 'Кисловодск');""")
    conn.commit()
    cur.close()
    conn.close()

# Вызов функций
create_db()
create_tbs()
insert_tbs()

