import requests
import json
import auxiliary_tools
from auxiliary_tools import logger, logging
from requests import Timeout
from decouple import config
from typing import Optional
from botrequest import history


headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': config('RAPID')
    }


@logging
def check_city(user_id: int, user_city: str) -> Optional[list]:
    """
    Функция по поиску введеного пользователем города из API Hotels.com.

    :param user_id: ID пользователя выполневшего данный запрос.
    :param user_city: Название города, введенного пользователем.
    """

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    user_locale, user_currency = history.user_setting(user_data=user_id)
    querystring = {"query": user_city, "locale": user_locale, "currency": user_currency}

    try:
        response_city_id = requests.request("GET", url,
                                            headers=headers,
                                            params=querystring,
                                            timeout=30.0)
        if response_city_id.status_code != 200:
            return None
    except Timeout as err:
        auxiliary_tools.logger.error(err)
        return None

    data = json.loads(response_city_id.text)
    entities = data['suggestions'][0]['entities']
    list_cities = []

    for entity in entities:
        if entity["type"] == "CITY":
            city_name = auxiliary_tools.del_span(entity["caption"])
            list_cities.append([city_name, entity["destinationId"]])

    logger.success('Данные от API Hotels.com успешно получены')

    return list_cities


@logging
def hotel_details(user_id: int, checkin: str, checkout: str, hotel_id: int, user_index: int):
    """
    Функция для полученния дополнительных данных об отеле из API Hotels.com.

    :param user_id: ID пользователя.
    :param checkin: Дата заезда пользователя.
    :param checkout: Дата выезда пользователя.
    :param hotel_id: ID интересующего нас отеля.
    :param user_index: Значение (0 или 1) в зависимости от запроса пользователя.
    """

    url = "https://hotels4.p.rapidapi.com/properties/get-details"

    user_locale, user_currency = history.user_setting(user_data=user_id)
    querystring = {'id': hotel_id, 'checkIn': checkin, 'checkOut': checkout,
                   'adults1': '1', 'locale': user_locale, 'currency': user_currency}

    try:
        hotel_details_response = requests.request("GET", url,
                                                  headers=headers,
                                                  params=querystring,
                                                  timeout=30.0)
        if hotel_details_response.status_code != 200:
            return None
    except Timeout as err:
        auxiliary_tools.logger.error(err)
        return None

    data = json.loads(hotel_details_response.text)
    cur_hotel_details = data['data']['body']['overview']['overviewSections'][user_index]['content']

    logger.success('Данные от API Hotels.com успешно получены')

    return cur_hotel_details
