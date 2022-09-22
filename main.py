from bot import bot
from botrequest.history import sql_table
from auxiliary_tools import logger


if __name__ == '__main__':
    try:
        sql_table()
        bot.polling(non_stop=True)
    except Exception as err:
        logger.error(err)
