import sqlite3


def sql_table():
    conn = sqlite3.connect('history.sqlite')
    cur_table = conn.cursor()
    cur_table.execute('CREATE TABLE IF NOT EXISTS users(user_id INT, locate TEXT, currency TEXT);')
    cur_table.execute("CREATE TABLE IF NOT EXISTS user_history(user_id INT, command TEXT, command_date TEXT,"
                      " command_time TEXT, hotel_id INT, hotel_name TEXT, stars TEXT, address TEXT,"
                      " distance TEXT, price TEXT);")
    conn.commit()
    conn.close()


def data_recording(user_data: tuple):
    conn = sqlite3.connect('history.sqlite')
    cur_data_recording = conn.cursor()
    if len(user_data) == 3:
        sql_select_request = 'INSERT INTO users VALUES(?, ?, ?);'
    else:
        sql_select_request = 'INSERT INTO user_history VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
    cur_data_recording.execute(sql_select_request, user_data)
    conn.commit()
    conn.close()


def from_users() -> list:
    conn = sqlite3.connect('history.sqlite')
    cur_users = conn.cursor()
    sql_select_request = 'SELECT user_id FROM users;'
    cur_users.execute(sql_select_request)
    all_result = cur_users.fetchall()
    conn.close()
    all_users = [hist_user_id[0] for hist_user_id in all_result]
    return all_users


def get_hotel(user_data: tuple) -> tuple:
    conn = sqlite3.connect('history.sqlite')
    cur_users = conn.cursor()
    sql_select_request = '''SELECT hotel_name, stars, address, distance, price FROM user_history 
    WHERE user_id=? and command_date=? and command_time=? and hotel_id=?;'''
    cur_users.execute(sql_select_request, user_data)
    result = cur_users.fetchone()
    conn.close()
    return result


def last_history(user_data: tuple) -> list:
    conn = sqlite3.connect('history.sqlite')
    cur_users = conn.cursor()
    sql_select_request = '''SELECT DISTINCT command_date, command_time FROM user_history WHERE user_id = ? 
    ORDER BY command_date DESC, command_time DESC;'''
    cur_users.execute(sql_select_request, (user_data,))
    result = cur_users.fetchmany(3)
    conn.close()
    return result


def hotel_history(user_data: tuple) -> list:
    conn = sqlite3.connect('history.sqlite')
    cur_users = conn.cursor()
    sql_select_request = '''SELECT command, hotel_name, stars, address, distance, price FROM user_history
    WHERE user_id=? and command_date=? and command_time=?;'''
    cur_users.execute(sql_select_request, user_data)
    result = cur_users.fetchall()
    conn.close()
    return result


def user_setting(user_data: int) -> tuple:
    conn = sqlite3.connect('history.sqlite')
    cur_users = conn.cursor()
    sql_select_request = '''SELECT locate, currency FROM users WHERE user_id = ?;'''
    cur_users.execute(sql_select_request, (user_data,))
    result = cur_users.fetchone()
    conn.close()
    return result


def user_locale(user_data: int) -> tuple:
    conn = sqlite3.connect('history.sqlite')
    cur_users = conn.cursor()
    sql_select_request = '''SELECT locate FROM users WHERE user_id = ?;'''
    cur_users.execute(sql_select_request, (user_data,))
    result = cur_users.fetchone()
    conn.close()
    return result


def user_currency(user_data: int) -> tuple:
    conn = sqlite3.connect('history.sqlite')
    cur_users = conn.cursor()
    sql_select_request = '''SELECT currency FROM users WHERE user_id = ?;'''
    cur_users.execute(sql_select_request, (user_data,))
    result = cur_users.fetchone()
    conn.close()
    return result


def user_locate_update(user_data: tuple) -> None:
    conn = sqlite3.connect('history.sqlite')
    cur_users = conn.cursor()
    sql_select_request = '''UPDATE users SET locate = ? WHERE locate = ? and user_id = ?;'''
    cur_users.execute(sql_select_request, user_data)
    conn.commit()
    conn.close()


def user_currency_update(user_data: tuple) -> None:
    conn = sqlite3.connect('history.sqlite')
    cur_users = conn.cursor()
    sql_select_request = '''UPDATE users SET currency = ? WHERE currency = ? and user_id = ?;'''
    cur_users.execute(sql_select_request, user_data)
    conn.commit()
    conn.close()
