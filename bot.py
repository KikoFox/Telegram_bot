import telebot
from telebot import types
from botrequest import lowprice, highprice, bestdeal, search, history
from users import User
import auxiliary_tools
from auxiliary_tools import logging
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta
from decouple import config
from collections.abc import Iterable


def listener(message: Iterable) -> None:
    """
    Когда приходят новые сообщения, то TeleBot вызывает эту функцию.
    """
    for m in message:
        if m.content_type == 'text':
            print(f'{m.chat.first_name} [{m.chat.id}]: {m.text}')


bot = telebot.TeleBot(config('TOKEN'))
bot.set_update_listener(listener)


commands = {
    'lowprice': 'Вывод самых дешевых отелей в городе',
    'highprice': 'Вывод самых дорогих отелей в городе',
    'bestdeal': 'Вывод отелей, наиболее подходящих по цене и расположению от центра',
    'history': 'Вывод истории поиска отелей',
    'setting': 'Настройка языка(название отеля, расстояние) и валюты результатов поиска'
}


@bot.message_handler(content_types=['text'])
def start(message: telebot.types.Message) -> None:
    """
    Функция распознования входящих сообщений

    """

    if message.text == '/start' or message.text.title() == 'Привет':
        command_start(message)
    elif message.text == '/help':
        command_help(message)
    elif message.text == '/lowprice':
        user = User.get_user(message.from_user.id)
        user.sorting = 'lowprice'
        bot.send_message(message.from_user.id, 'Введите название города')
        bot.register_next_step_handler(message, get_locate)
    elif message.text == '/highprice':
        user = User.get_user(message.from_user.id)
        user.sorting = 'highprice'
        bot.send_message(message.from_user.id, 'Введите название города')
        bot.register_next_step_handler(message, get_locate)
    elif message.text == '/bestdeal':
        user = User.get_user(message.from_user.id)
        user.sorting = 'bestdeal'
        bot.send_message(message.from_user.id, 'Введите название города')
        bot.register_next_step_handler(message, get_locate)
    elif message.text == '/history':
        command_history(message)
    elif message.text == '/setting':
        command_setting(message)
    else:
        bot.send_message(message.from_user.id, 'Я Вас не понимаю.\nДля начала работы напишите /start')


@logging
def command_start(message: telebot.types.Message) -> None:
    """
    Начальная функция проверяющая ID написавшего пользователя с данными из базы данных
    и при его отсутвии регестрирует пользователя в данной базе данных.

    """

    user_id = int(message.from_user.id)
    sql_users = history.from_users()
    if sql_users == list():
        data = (user_id, 'ru_RU', 'RUB')
        history.data_recording(data)
    else:
        if user_id not in sql_users:
            data = (user_id, 'ru_RU', 'RUB')
            history.data_recording(data)
    bot.send_message(message.from_user.id, 'Здравствуйте. Я помогу Вам найти отель в любом городе.\n'
                                           'Для ознакомления с командами напишите /help')


@logging
def command_help(message: telebot.types.Message) -> None:
    """
    Функция, срабатывающая при использовании команды help пользователем.

    """

    User.add_user(message.from_user.id)
    user = User.get_user(message.from_user.id)
    user.user_id = message.from_user.id
    help_text = "Доступны следующие команды: \n"
    for key, value in commands.items():
        help_text += "/{}: {}\n".format(key, value)
    bot.send_message(message.from_user.id, help_text)


@logging
def command_history(message: telebot.types.Message) -> None:
    """
    Функция вывода истории поиска пользователя.

    """

    user = User.get_user(message.from_user.id)
    user_history = history.last_history(user_data=user.user_id)
    if user_history != list():
        for date_time in user_history:
            cur_date, cur_time = date_time
            data = (user.user_id, cur_date, cur_time)
            all_history_hotels = history.hotel_history(data)
            hist_text = 'Команда: {0}\nДата:   {1}  Время:   {2}\n\n'.format(
                all_history_hotels[0][0], cur_date, cur_time)
            for history_hotel in all_history_hotels:
                hist_text += '`{0}  {1} ⭐️\nАдрес: {2}\nВ {3} от центра города\n' \
                             '{4} за все время проживания `\n\n'.format(history_hotel[1], history_hotel[2],
                                                                        history_hotel[3], history_hotel[4],
                                                                        history_hotel[5])
            history_text = auxiliary_tools.text_formatting(hist_text)
            bot.send_message(message.from_user.id, text=history_text, parse_mode='MarkdownV2')
    else:
        bot.send_message(message.from_user.id, 'Ваша история запросов пуста')
    bot.send_message(message.from_user.id, 'Для нового запроса используйте команду /help')


@logging
def command_setting(message: telebot.types.Message) -> None:
    """
    Функция настройки языка и валюты получаемой из API Hotels.com.

    """

    language = types.InlineKeyboardMarkup()
    language_russian = types.InlineKeyboardButton(text='Русский', callback_data='1_lang')
    language_english = types.InlineKeyboardButton(text='Английский', callback_data='2_lang')
    language.add(language_russian, language_english)
    bot.send_message(message.from_user.id, text='Выберите язык', reply_markup=language)


@logging
def get_locate(message: telebot.types.Message) -> None:
    """
    Функция для поиска введенного пользователем города и вывод найденых вариантов в чат.

    """

    city_data = search.check_city(user_id=message.from_user.id, user_city=message.text)
    if city_data == list():
        bot.send_message(chat_id=message.from_user.id, text='Введенный вами город не найден.\nВведите название города')
        bot.register_next_step_handler(message, get_locate)
    elif city_data is None:
        bot.send_message(chat_id=message.from_user.id, text='Сервис временно не доступен. Попробуйте чуть позже')
    else:
        cites = types.InlineKeyboardMarkup()
        for data in city_data:
            name, city_id = data
            button = types.InlineKeyboardButton(text=name, callback_data=f'{city_id}_city')
            cites.add(button)
        bot.send_message(chat_id=message.from_user.id, text='Найдены следущие города: ', reply_markup=cites)


@logging
def price_range(message: telebot.types.Message) -> None:
    """
    Функция для определения диапазона цен вводимых пользователем.

    """

    user = User.get_user(message.from_user.id)
    user_price = auxiliary_tools.corrected_price(message.text).split('-')
    if len(user_price) == 1:
        if not user_price[0].isdigit():
            bot.send_message(chat_id=message.from_user.id, text='Пожалуйста, введите цены цифрами')
            bot.register_next_step_handler(message, price_range)
        else:
            user_price.insert(0, '0')
    else:
        for current_price in user_price:
            if not current_price.isdigit():
                bot.send_message(chat_id=message.from_user.id, text='Пожалуйста, введите цены цифрами')
                bot.register_next_step_handler(message, price_range)
                break
        if int(user_price[0]) > int(user_price[1]):
            user_price.reverse()
    user.low_high_price = user_price
    bot.send_message(chat_id=message.from_user.id,
                     text='Введите максимальное расстояние от центра города в км (без км)')
    bot.register_next_step_handler(message, distance_range)


@logging
def distance_range(message: telebot.types.Message) -> None:
    """
    Функция для определения максимальной удаленности от центра города пользователем.

    """

    user = User.get_user(message.from_user.id)
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, 'Пожалуйста, введите расстояние от центра города в км цифрами')
        bot.register_next_step_handler(message, distance_range)
    else:
        user.max_distance = float(message.text)
    checkin(user_id=user.user_id)


@logging
def checkin(user_id: int) -> None:
    """
    Функция интеграции календаря в чат пользователя и получение даты заезда.

    """

    bot.send_message(user_id, 'Выберите дату заезда')
    calendar, step = DetailedTelegramCalendar(
        calendar_id=1,
        current_date=date.today(),
        min_date=date.today(),
        max_date=date.today() + timedelta(days=365),
        locale='ru'
    ).build()
    bot.send_message(user_id, f"Выберите {LSTEP[step]}", reply_markup=calendar)


@logging
def count_hotel(message: telebot.types.Message) -> None:
    """
    Функция для получения количества отелей пользователем.

    """

    if not message.text.isdigit():
        bot.send_message(chat_id=message.from_user.id, text='Пожалуйста, введите количество отелей цифрами')
        bot.register_next_step_handler(message, count_hotel)
    elif int(message.text) > 10:
        bot.send_message(chat_id=message.from_user.id, text='Вы ввели больше отелей, чем возможно. Повторите ввод')
        bot.register_next_step_handler(message, count_hotel)
    else:
        user = User.get_user(message.from_user.id)
        user.count = int(message.text)
        photo_selection = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        button_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        photo_selection.add(button_yes, button_no)
        bot.send_message(message.from_user.id, text='Выводить фотографии?', reply_markup=photo_selection)


@logging
def count_hotel_photo(message: telebot.types.Message) -> None:
    """
    Функция дял получения количества фотографий отеля пользователем.

    """

    if not message.text.isdigit():
        bot.send_message(message.from_user.id, 'Пожалуйста, введите количество фотографий цифрами')
        bot.register_next_step_handler(message, count_hotel_photo)
    elif int(message.text) > 5:
        bot.send_message(message.from_user.id, 'Вы ввели количество фотографий больше, чем возможно. Повторите ввод')
        bot.register_next_step_handler(message, count_hotel_photo)
    else:
        user = User.get_user(message.from_user.id)
        user.count_image = int(message.text)
        get_result(user_id=user.user_id)


@logging
def get_result(user_id: int) -> None:
    """
    По введеным данным выполняется запрос к API Hotels.com

    """

    user = User.get_user(user_id)
    bot.send_message(user_id, '⏳ Веду поиск подходящих отелей..')
    now_date, now_time = auxiliary_tools.get_date_time(user_id)
    count_days = (user.checkout - user.checkin).days
    if user.sorting == 'lowprice':
        hotel_list = lowprice.properties_list(user_id=user.user_id, id_city=user.city_id, hotel_count=user.count,
                                              checkin=user.checkin, checkout=user.checkout,
                                              count_photo=user.count_image, get_photo=user.get_photo)
    elif user.sorting == 'highprice':
        hotel_list = highprice.properties_list(user_id=user.user_id, id_city=user.city_id, hotel_count=user.count,
                                               checkin=user.checkin, checkout=user.checkout,
                                               count_photo=user.count_image, get_photo=user.get_photo)
    elif user.sorting == 'bestdeal':
        hotel_list = bestdeal.properties_list(user_id=user.user_id, id_city=user.city_id, hotel_count=user.count,
                                              checkin=user.checkin, checkout=user.checkout,
                                              min_price=int(user.low_high_price[0]),
                                              max_price=int(user.low_high_price[1]), max_distance=user.max_distance,
                                              count_photo=user.count_image, get_photo=user.get_photo)
    else:
        hotel_list = list()
    if hotel_list is None:
        bot.send_message(user_id, 'Сервис временно не доступен. Попробуйте чуть позже')
    else:
        if user.get_photo:
            for hotel in hotel_list:
                bot.send_media_group(chat_id=user.user_id, media=hotel[6])
                print_result(user_id=user.user_id, sorting=user.sorting, current_date=now_date, current_time=now_time,
                             hotel_id=hotel[0], hotel_name=hotel[1], hotel_star=hotel[2], hotel_address=hotel[3],
                             hotel_distance=hotel[4], hotel_price=hotel[5], count_days=count_days)
        else:
            for hotel in hotel_list:
                print_result(user_id=user.user_id, sorting=user.sorting, current_date=now_date, current_time=now_time,
                             hotel_id=hotel[0], hotel_name=hotel[1], hotel_star=hotel[2], hotel_address=hotel[3],
                             hotel_distance=hotel[4], hotel_price=hotel[5], count_days=count_days)
        if len(hotel_list) == 0:
            bot.send_message(user.user_id, 'По вашему запросу ничего не найдено')
        elif len(hotel_list) < int(user.count):
            bot.send_message(user.user_id, 'Нашлось меньше, чем вы запрашивали')
        else:
            bot.send_message(user.user_id, 'Поиск завершён')
        bot.send_message(user.user_id, 'Для нового запроса используйте команду /help')


@logging
def print_result(user_id: int, sorting: str, current_date: str, current_time: str, hotel_id: int, hotel_name: str,
                 hotel_star: str, hotel_address: str, hotel_distance: str, hotel_price: str, count_days: int) -> None:
    """
    Вывод полученных данных от API Hotels.com
    и запись результатов поиска в базу данных.

    """

    data = (user_id, sorting, current_date, current_time, hotel_id, hotel_name, hotel_star, hotel_address,
            hotel_distance, hotel_price)
    history.data_recording(data)
    cur_hotel = types.InlineKeyboardMarkup(row_width=2)
    button_book_a_room = types.InlineKeyboardButton(text='Перейти на сайт',
                                                    url=f'https://ru.hotels.com/ho{hotel_id}')
    button_look_nearby = types.InlineKeyboardButton(text='Поблизости', callback_data=f'{hotel_id}_around')
    button_more = types.InlineKeyboardButton(text='Подробнее', callback_data=f'{hotel_id}_more')
    cur_hotel.add(button_book_a_room, button_look_nearby, button_more)
    if count_days <= 1:
        text = '*{0}*  *{1}* ⭐️\nАдрес: _{2}_\nВ *{3}* от центра города\n*{4}* за 1 ночь\n'.format(
            hotel_name, hotel_star, hotel_address, hotel_distance, hotel_price)
    elif 1 < count_days <= 4:
        text = '*{0}*  *{1}* ⭐️\nАдрес: _{2}_\nВ *{3}* от центра города\n*{4}* за {5} ночи\n'.format(
            hotel_name, hotel_star, hotel_address, hotel_distance, hotel_price, count_days)
    else:
        text = '*{0}*  *{1}* ⭐️\nАдрес: _{2}_\nВ *{3}* от центра города\n*{4}* за {5} ночей\n'.format(
            hotel_name, hotel_star, hotel_address, hotel_distance, hotel_price, count_days)
    answer = auxiliary_tools.text_formatting(text)
    bot.send_message(user_id, text=answer, reply_markup=cur_hotel, parse_mode='MarkdownV2')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
@logging
def callback_first_calendar(call: telebot.types.CallbackQuery) -> None:
    """
    Функция обратного вызова для календаря заезда.

    """

    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today(),
                                                 locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберете {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        user = User.get_user(call.from_user.id)
        user.checkin = result
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)

        bot.send_message(user.user_id, 'Выберите дату выезда')
        calendar, step = DetailedTelegramCalendar(
            calendar_id=2,
            min_date=date.today(),
            max_date=result + timedelta(days=365),
            locale='ru'
        ).build()
        bot.send_message(user.user_id, f"Выберите {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
@logging
def callback_second_calendar(call: telebot.types.CallbackQuery) -> None:
    """
    Функция обратного вызова для календаря выезда

    """

    user = User.get_user(call.from_user.id)
    result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=user.checkin,
                                                 locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберете {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        user.checkout = result
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)
        bot.send_message(call.from_user.id, 'Сколько отелей показать?(не более 10)')
        bot.register_next_step_handler(call.message, count_hotel)


@bot.callback_query_handler(func=lambda call: True)
@logging
def callback(call: telebot.types.CallbackQuery) -> None:
    """
    Функция обратного вызова для всех inline-кнопок, исключая календари.

    """

    user = User.get_user(call.from_user.id)
    if call.data.endswith('around'):
        user.around = True
        count_days = (user.checkout - user.checkin).days
        hotel_id = auxiliary_tools.get_the_number(call.data)
        my_hotel = auxiliary_tools.get_user_hotel_data(user_id=user.user_id, cur_hotel_id=hotel_id)
        if count_days <= 1:
            text = '*{0}*  *{1}* ⭐️\nАдрес: _{2}_\nВ *{3}* от центра города\n*{4}* за 1 ночь\n'.format(
                my_hotel[0], my_hotel[1], my_hotel[2], my_hotel[3], my_hotel[4])
        elif 1 < count_days <= 4:
            text = '*{0}*  *{1}* ⭐️\nАдрес: _{2}_\nВ *{3}* от центра города\n*{4}* за {5} ночи\n'.format(
                my_hotel[0], my_hotel[1], my_hotel[2], my_hotel[3], my_hotel[4], count_days)
        else:
            text = '*{0}*  *{1}* ⭐️\nАдрес: _{2}_\nВ *{3}* от центра города\n*{4}* за {5} ночей\n'.format(
                my_hotel[0], my_hotel[1], my_hotel[2], my_hotel[3], my_hotel[4], count_days)
        around_hotel = types.InlineKeyboardMarkup()
        if user.more:
            cur_text = auxiliary_tools.text_back(user_list=my_hotel, count_days=count_days, user_text=call.message.text)
            text += cur_text
            button_book_a_room = types.InlineKeyboardButton(text='Перейти на сайт',
                                                            url=f'https://ru.hotels.com/ho{hotel_id}')
            around_hotel.add(button_book_a_room)
            user.around = False
            user.more = False
        else:
            button_book_a_room = types.InlineKeyboardButton(text='Перейти на сайт',
                                                            url=f'https://ru.hotels.com/ho{hotel_id}')
            button_more = types.InlineKeyboardButton(text='Подробнее', callback_data=f'{hotel_id}_more')
            around_hotel.add(button_book_a_room, button_more)
        details = search.hotel_details(user_id=user.user_id, checkin=user.checkin, checkout=user.checkout,
                                       hotel_id=hotel_id, user_index=1)
        if details is None:
            text += 'Сервис временно не доступен. Попробуйте чуть позже'
        else:
            text += "\n\nЧто интересного поблизости:\n\n"
            for place in details:
                text += ('• ' + place + '\n')
        answer = auxiliary_tools.text_formatting(text)
        bot.edit_message_text(text=answer, chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=around_hotel, parse_mode='MarkdownV2')
    elif call.data.endswith('more'):
        user.more = True
        count_days = (user.checkout - user.checkin).days
        hotel_id = auxiliary_tools.get_the_number(call.data)
        my_hotel = auxiliary_tools.get_user_hotel_data(user_id=user.user_id, cur_hotel_id=hotel_id)
        if count_days <= 1:
            text = '*{0}*  *{1}* ⭐️\nАдрес: _{2}_\nВ *{3}* от центра города\n*{4}* за 1 ночь\n'.format(
                my_hotel[0], my_hotel[1], my_hotel[2], my_hotel[3], my_hotel[4])
        elif 1 < count_days <= 4:
            text = '*{0}*  *{1}* ⭐️\nАдрес: _{2}_\nВ *{3}* от центра города\n*{4}* за {5} ночи\n'.format(
                my_hotel[0], my_hotel[1], my_hotel[2], my_hotel[3], my_hotel[4], count_days)
        else:
            text = '*{0}*  *{1}* ⭐️\nАдрес: _{2}_\nВ *{3}* от центра города\n*{4}* за {5} ночей\n'.format(
                my_hotel[0], my_hotel[1], my_hotel[2], my_hotel[3], my_hotel[4], count_days)
        more_hotel = types.InlineKeyboardMarkup()
        if user.around:
            cur_text = auxiliary_tools.text_back(user_list=my_hotel, count_days=count_days, user_text=call.message.text)
            text += cur_text
            button_book_a_room = types.InlineKeyboardButton(text='Перейти на сайт',
                                                            url=f'https://ru.hotels.com/ho{hotel_id}')
            more_hotel.add(button_book_a_room)
            user.around = False
            user.more = False
        else:
            button_book_a_room = types.InlineKeyboardButton(text='Перейти на сайт',
                                                            url=f'https://ru.hotels.com/ho{hotel_id}')
            button_look_nearby = types.InlineKeyboardButton(text='Поблизости', callback_data=f'{hotel_id}_around')
            more_hotel.add(button_book_a_room, button_look_nearby)
        all_services = search.hotel_details(user_id=user.user_id, checkin=user.checkin, checkout=user.checkout,
                                            hotel_id=hotel_id, user_index=0)
        if all_services is None:
            text += 'Сервис временно не доступен. Попробуйте чуть позже'
        else:
            text += "\n\nОсновные услуги и удобства:\n\n"
            for service in all_services:
                text += ('• ' + service + '\n')
        answer = auxiliary_tools.text_formatting(text)
        bot.edit_message_text(text=answer, chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=more_hotel, parse_mode='MarkdownV2')
    elif call.data.endswith('city'):
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user.city_id = auxiliary_tools.get_the_number(call.data)
        if user.sorting == 'bestdeal':
            bot.send_message(call.from_user.id, 'Введите желаемые цены через дефиз/пробел или укажите'
                                                ' максимальную цену для поиска')
            bot.register_next_step_handler(call.message, price_range)
        else:
            checkin(user_id=user.user_id)
    elif call.data == 'yes':
        user.get_photo = True
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Введите количество фотографий(не более 5)')
        bot.register_next_step_handler(call.message, count_hotel_photo)
    elif call.data == 'no':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        user = User.get_user(call.from_user.id)
        get_result(user_id=user.user_id)
    elif call.data.endswith('lang'):
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        number = auxiliary_tools.get_the_number(call.data)
        user_language = history.user_locale(call.from_user.id)
        if number == 1:
            if user_language[0] == 'ru_RU':
                pass
            else:
                data = ('ru_RU', user_language[0], call.from_user.id)
                history.user_locate_update(user_data=data)
        elif number == 2:
            if user_language[0] == 'en_US':
                pass
            else:
                data = ('en_US', user_language[0], call.from_user.id)
                history.user_locate_update(user_data=data)
        currency = types.InlineKeyboardMarkup()
        currency_usd = types.InlineKeyboardButton(text='Доллар', callback_data='1_currency')
        currency_eur = types.InlineKeyboardButton(text='Евро', callback_data='2_currency')
        currency_rub = types.InlineKeyboardButton(text='Рубль', callback_data='3_currency')
        currency.add(currency_usd, currency_eur, currency_rub)
        bot.send_message(text='Выберите валюту', chat_id=call.message.chat.id, reply_markup=currency)
    elif call.data.endswith('currency'):
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        number = auxiliary_tools.get_the_number(call.data)
        user_currency = history.user_currency(call.from_user.id)
        if number == 1:
            if user_currency[0] == 'USD':
                pass
            else:
                data = ('USD', user_currency[0], call.from_user.id)
                history.user_currency_update(user_data=data)
        elif number == 2:
            if user_currency[0] == 'EUR':
                pass
            else:
                data = ('EUR', user_currency[0], call.from_user.id)
                history.user_currency_update(user_data=data)
        elif number == 3:
            if user_currency[0] == 'RUB':
                pass
            else:
                data = ('RUB', user_currency[0], call.from_user.id)
                history.user_currency_update(user_data=data)
        bot.send_message(call.from_user.id, 'Изменения сохранены')
        bot.send_message(call.from_user.id, 'Для нового запроса используйте команду /help')
