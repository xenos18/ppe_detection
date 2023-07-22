import sqlite3


def connect_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


class DataBase:
    def __init__(self, database=None):
        if database is None:
            database = sqlite3.connect("bot/database.db", check_same_thread=False)
            database.row_factory = sqlite3.Row
        self.__db = database
        self.__cur = database.cursor()

    def add_user(self, telegram_id, last_usage):
        try:
            self.__cur.execute("INSERT INTO users VALUES (?, ?, ?)",
                               (telegram_id, 0, last_usage))
            self.__db.commit()
        except Exception as e:
            print('Ошибка добавления в БД', e)
            return False
        return True

    def add_usage(self, telegram_id, usages, last_usage):
        try:
            promt = f"UPDATE users SET usages = '{usages}', last_usage = '{last_usage}' WHERE telegram_id = '{telegram_id}'"
            self.__cur.execute(promt)
            self.__db.commit()
        except Exception as e:
            print('Ошибка изменения в БД', e)
            return False
        return True

    def get_user(self, telegram_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE telegram_id = '{telegram_id}'")
            return self.__cur.fetchall()
        except Exception as e:
            print('Ошибка получения члена из БД', e)
            return False
