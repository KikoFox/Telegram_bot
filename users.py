class User:
    """
    Класс Пользователь. Содерит все необходимые параметры для поиска и работы в рамках сессии.
    """

    users = dict()

    def __init__(self):
        self.__user_id: int = 1
        self.__user_date: str = '2022-01-01'
        self.__user_time: str = '00:00:00'
        self.__city_id: int = 1
        self.__checkin: str = '2022-01-01'
        self.__checkout: str = '2022-01-01'
        self.__count: int = 5
        self.__count_image: int = 3
        self.__sorting: str = 'None'
        self.__low_high_price: list = ['None', 'None']
        self.__max_distance: float = 2
        self.__get_photo: bool = False
        self.__around: bool = False
        self.__more: bool = False

    @classmethod
    def get_user(cls, id_user):
        if id_user in cls.users.keys():
            return cls.users[id_user]
        else:
            return cls.add_user(id_user)

    @classmethod
    def add_user(cls, id_user):
        cls.users[id_user] = User()
        return cls.users[id_user]

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, cur_user_id):
        self.__user_id = cur_user_id

    @property
    def user_date(self):
        return self.__user_date

    @user_date.setter
    def user_date(self, cur_user_date):
        self.__user_date = cur_user_date

    @property
    def user_time(self):
        return self.__user_time

    @user_time.setter
    def user_time(self, cur_user_time):
        self.__user_time = cur_user_time

    @property
    def city_id(self):
        return self.__city_id

    @city_id.setter
    def city_id(self, cur_city_id):
        self.__city_id = cur_city_id

    @property
    def checkin(self):
        return self.__checkin

    @checkin.setter
    def checkin(self, cur_checkin):
        self.__checkin = cur_checkin

    @property
    def checkout(self):
        return self.__checkout

    @checkout.setter
    def checkout(self, cur_checkout):
        self.__checkout = cur_checkout

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, cur_count):
        self.__count = cur_count

    @property
    def count_image(self):
        return self.__count_image

    @count_image.setter
    def count_image(self, cur_count_image):
        self.__count_image = cur_count_image

    @property
    def sorting(self):
        return self.__sorting

    @sorting.setter
    def sorting(self, cur_sorting):
        self.__sorting = cur_sorting

    @property
    def low_high_price(self):
        return self.__low_high_price

    @low_high_price.setter
    def low_high_price(self, cur_low_high_price):
        self.__low_high_price = cur_low_high_price

    @property
    def max_distance(self):
        return self.__max_distance

    @max_distance.setter
    def max_distance(self, cur_max_distance):
        self.__max_distance = cur_max_distance

    @property
    def get_photo(self):
        return self.__get_photo

    @get_photo.setter
    def get_photo(self, cur_get_photo):
        self.__get_photo = cur_get_photo

    @property
    def around(self):
        return self.__around

    @around.setter
    def around(self, cur_around):
        self.__around = cur_around

    @property
    def more(self):
        return self.__more

    @more.setter
    def more(self, cur_more):
        self.__more = cur_more
