# -*- coding: utf-8 -*-

from server import run_app, get, post, serve_static_file, Response
from db import insert_comment_tb, get_json_from_db, select_all, \
    select_filter_all, delete_row, select_filter, update_tb, update_comment_col
import os
import json
from validators import validation_email, validation_phone, not_empty_test
from datetime import datetime

__author__ = 'Artem Kraynev'

MY_ROOT = os.path.join(os.path.dirname(__file__), 'media')


@get('/')
def index(request):
    """
    Главная страница
    """
    return open('template/index.html').read()


@get('/form=(?P<form_num>\d+)')
def get_form(request, form_num):
    """
    Страница просмотра формы
    """
    return open('template/edit_comment.html').read()


@get('/comment')
def comment_form(request):
    """
    Страница заполения формы
    """
    return open('template/comment.html').read()


@get('/view')
def view(request):
    """
    Страница просмотра комментариев
    """
    return open('template/view.html').read()


@get('/stat')
def statistics(request):
    """
    Страница просмотра статистики
    комментариев по регионам
    """
    return open('template/statistics.html').read()


@get('/stat=(?P<region_num>\d+)')
def get_form(request, region_num):
    """
    Страница просмотра статистики
    комментариев по городам
    """
    return open('template/stat_city.html').read()


@get('/del_com=(?P<com_num>\d+)')
def get_form(request, com_num):
    """
    Удаление комментариев
    """
    update_comment_col(com_num)
    return open('template/view.html').read()


@post('/set_comment')
def set_comment(request):
    """
    Отправка формы
    """

    if request.POST:
        r = request.POST
        surname = get_item(r, 'surname')
        name = get_item(r, 'nameF')
        middle_name = get_item(r, 'middle_name')
        region = get_item(r, 'region')
        city = get_item(r, 'city')
        phone = get_item(r, 'phone')
        email = get_item(r, 'email')
        comment = get_item(r, 'comment')

        email_valid = validation_email(email=email)
        phone_valid = validation_phone(phone=phone)

        fields = [surname, name, middle_name, region, city, comment]
        other_fields_valid = not_empty_test(fields=fields)

        now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

        if email_valid and phone_valid and other_fields_valid:
            insert_comment_tb(
                date=now,
                surname=surname,
                name=name,
                middle_name=middle_name,
                region=region,
                city=city,
                phone=phone,
                email=email,
                comment=comment
            )
            id_val_region_list = select_filter(
                req_row='id',
                row_name='region',
                row_val=region,
                db_name='region'
            )
            id_val_region = id_val_region_list[0][0]
            update_tb(
                db_name='region',
                id_val=id_val_region
            )

            id_val_city_list = select_filter(
                req_row='id',
                row_name='city',
                row_val=city,
                db_name='city'
            )
            id_val_city = id_val_city_list[0][0]
            update_tb(
                db_name='city',
                id_val=id_val_city
            )

            return open('template/form_is_completed.html').read()


@post('/del_comment')
def del_comment(request):
    """
    Удаление формы
    """
    if request.POST:
        id_val = int(get_item(request.POST, 'idVal'))
        delete_row(
            row_name='id',
            row_val=id_val,
            db_name="comment"
        )
        return open('template/form_is_completed.html').read()


@get('/json')
def send_json(request):
    """
    Отправка JSON со всеми заполнеными формами
    """
    json_obj = select_all(db_name='comment')
    json_dict = {}
    j = 0
    for fields in json_obj:
        j += 1
        json_dict[str(j)] = fields
    return Response(
        json.dumps(json_dict),
        content_type='application/json'
    )


@get('/comment/json')
def send_json_comment_form(request):
    """
    Отправка JSON с регионами и городами
    """
    json_obj = get_json_from_db()
    return Response(
        json.dumps(json_obj),
        content_type='application/json'
    )


@get('/form=(?P<form_num>\d+)/json')
def send_json_form(request, form_num):
    """
    Отправка JSON с выбранной формой
    """
    json_obj = select_filter_all(
        row_name='id',
        row_val=form_num,
        db_name="comment"
    )
    return Response(
        json.dumps(json_obj),
        content_type='application/json'
    )


@get('/view/json')
def send_json_form(request):
    """
    Отправка JSON с комментариями
    """
    json_obj = []
    query_list = select_all(db_name="comment")
    for i in query_list:
        json_obj.append([i[0], i[7]])
    return Response(
        json.dumps(json_obj),
        content_type='application/json'
    )


@get('/stat/json')
def send_json_stat(request):
    """
    Отправка JSON со статистикой комментариев по регионам
    """
    json_obj = []
    query_list = select_all('region')
    for i in query_list:
        if i[2] > 5:
            json_obj.append(i)
    return Response(
        json.dumps(json_obj),
        content_type='application/json'
    )


@get('/stat=(?P<city_num>\d+)/json')
def send_json_stat_city(request, city_num):
    """
    Отправка JSON со статистикой комментариев по городам
    """
    json_obj = select_filter_all(
        row_name='region_id',
        row_val=city_num,
        db_name="city"
    )
    return Response(
        json.dumps(json_obj),
        content_type='application/json'
    )


@get('/media/(?P<filename>.+)')
def media(request, filename):
    """
    Подрузка файлов из директории media
    """
    return serve_static_file(request, filename, root=MY_ROOT)


# Маленький невидимый такой костылек
def get_item(obj, attr):
    a = obj.__getitem__(attr)
    return a

run_app()


