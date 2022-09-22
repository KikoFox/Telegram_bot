import re
import os
from botrequest import history
from datetime import date
import time
from users import User
from loguru import logger
import functools


logger.add(os.path.join('logging', 'correct_work.log'),
           encoding='utf-8', format='{time} | {level} | {message}',
           level='DEBUG')


def logging(func):

    def wrapped_func(*args, **kwargs):
        logger.info(f'Запускается функция {func.__name__}')
        value = func(*args, **kwargs)
        return value
    return wrapped_func


def get_the_number(user_text: str) -> int:
    pattern = r'\d+'
    result = re.findall(pattern, user_text)
    return int(result[0])


def text_formatting(user_text: str) -> str:
    result_1 = re.sub(r'[.]', '\.', user_text)
    result_2 = re.sub(r'[-]', '\-', result_1)
    result_3 = re.sub(r'[(]', '\(', result_2)
    result_4 = re.sub(r'[)]', '\)', result_3)
    result_5 = re.sub(r'[+]', '\+', result_4)
    result_6 = re.sub(r'[|]', '\|', result_5)
    result_7 = re.sub(r'[!]', '\!', result_6)
    return result_7


def text_back(user_list: tuple, count_days: int, user_text: str) -> str:
    if count_days <= 1:
        pattern = '{0}  {1} ⭐️\nАдрес: {2}\nВ {3} от центра города\n{4} за 1 ночь\n'.format(
            user_list[0], user_list[1], user_list[2], user_list[3], user_list[4])
    elif 1 < count_days <= 4:
        pattern = '{0}  {1} ⭐️\nАдрес: {2}\nВ {3} от центра города\n{4} за {5} ночи\n'.format(
            user_list[0], user_list[1], user_list[2], user_list[3], user_list[4], count_days)
    else:
        pattern = '{0}  {1} ⭐️\nАдрес: {2}\nВ {3} от центра города\n{4} за {5} ночей\n'.format(
            user_list[0], user_list[1], user_list[2], user_list[3], user_list[4], count_days)
    must_be = ''
    first = re.sub(pattern, must_be, user_text)
    second = re.sub(r'\\-', '-', first)
    result = re.sub(r'\\.', '.', second)
    return result


def get_user_hotel_data(user_id: int, cur_hotel_id: int) -> tuple:
    user = User.get_user(user_id)
    user_date = user.user_date
    user_time = user.user_time
    data = (user_id, user_date, user_time, cur_hotel_id)
    cur_hotel = history.get_hotel(data)
    return cur_hotel


def get_date_time(user_id: int) -> tuple[str, str]:
    user = User.get_user(user_id)
    now = date.today()
    now_date = now.strftime('%d-%m-%Y')
    user.user_date = now_date
    now_time = time.strftime('%H:%M:%S')
    user.user_time = now_time
    return now_date, now_time


def del_span(user_text: str) -> str:

    pattern_1 = r"<span class='highlighted'>"
    pattern_2 = r"</span>"
    replacement = ''

    result_1 = re.sub(pattern_1, replacement, user_text)
    result_2 = re.sub(pattern_2, replacement, result_1)

    return result_2


def clear_photo(url_photo: str) -> str:

    pattern = r'{size}'
    replacement = 'z'

    result = re.sub(pattern, replacement, url_photo)

    return result


def existing_address(hotel: dict) -> str:
    try:
        hotel_address = hotel['address']['streetAddress']
    except Exception as err:
        hotel_address = 'Пожалуйста уточните адрес на сайте'
        logger.error(err)
    return hotel_address


def corrected_price(price: str) -> str:

    pattern = r" "
    replacement = '-'

    result = re.sub(pattern, replacement, price)

    return result
