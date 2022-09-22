import requests
import json
import auxiliary_tools
from auxiliary_tools import logging, logger
from telebot.types import InputMediaPhoto
from decouple import config
from botrequest import history
from requests import Timeout
from typing import Optional


headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': config('RAPID')
    }


@logging
def properties_list(user_id: int, id_city: str, hotel_count: int, checkin: str, checkout: str, count_photo: int,
                    get_photo: bool) -> Optional[list[tuple]]:
    """
    Функция для запроса данных из API Hotels.com

    :param user_id: ID пользователя выполневшего данный запрос.
    :param id_city: ID города в котором необходимо найти отели.
    :param hotel_count: Количество запрашиваемых пользователем отелей.
    :param checkin: Дата заезда, выбранная пользователем.
    :param checkout: Дата выезда, выбранная пользователем.
    :param count_photo: Количество запрашиваемых пользователем фотографий.
    :param get_photo: Булевое значение, указывающее необходимость вывода фотографий или нет.

    """

    url = "https://hotels4.p.rapidapi.com/properties/list"

    user_locale, user_currency = history.user_setting(user_data=user_id)

    querystring = {"destinationId": id_city, "pageNumber": '1', "pageSize": hotel_count,
                   "checkIn": checkin, "checkOut": checkout,
                   "adults1": "1", "sortOrder": "PRICE", "locale": user_locale,
                   "currency": user_currency}

    try:
        response_list_hotel = requests.request("GET", url,
                                               headers=headers,
                                               params=querystring,
                                               timeout=30.0)
        if response_list_hotel.status_code != 200:
            return None
    except Timeout as end_time:
        auxiliary_tools.logger.error(end_time)
        return None

    data = json.loads(response_list_hotel.text)

    if get_photo:
        all_list_hotel = [
            (
                hotel['id'],
                hotel['name'],
                str(hotel['starRating']),
                auxiliary_tools.existing_address(hotel),
                hotel['landmarks'][0]['distance'],
                hotel['ratePlan']['price']['current'],
                hotel_list_photo(hotel['id'], count_photo)
            )
            for hotel in data['data']['body']['searchResults']['results']
        ]
    else:
        all_list_hotel = [
            (
                hotel['id'],
                hotel['name'],
                str(hotel['starRating']),
                auxiliary_tools.existing_address(hotel),
                hotel['landmarks'][0]['distance'],
                hotel['ratePlan']['price']['current']
            )
            for hotel in data['data']['body']['searchResults']['results']
        ]

    logger.success('Данные от API Hotels.com успешно получены')

    return all_list_hotel


@logging
def hotel_list_photo(hotel_id: int, count_photo: int) -> list[InputMediaPhoto]:
    """
    Функция получения фотографии по ID отеля из API Hotels.com.

    :param hotel_id: ID отеля конкретного отеля.
    :param count_photo: Количество фотографий, запрошенных пользователем.
    """

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {'id': hotel_id}

    hotel_photo = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(hotel_photo.text)

    if len(data['hotelImages']) < count_photo:
        count_photo = len(data['hotelImages'])

    photo = [auxiliary_tools.clear_photo(image['baseUrl']) for image in data['hotelImages']][:count_photo]
    result = [InputMediaPhoto(media=url, caption=f'Фотография №{number + 1}') for number, url in enumerate(photo)]

    return result
