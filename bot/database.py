import sqlite3


def connect_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД """
    db = connect_db()
    with open("sql_structure.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


class DataBase:
    def __init__(self, database=None):
        if database is None:
            database = sqlite3.connect("../bot/database.db", check_same_thread=False)
            database.row_factory = sqlite3.Row
        self.__db = database
        self.__cur = database.cursor()

    def add_user(self, telegram_id, username, balance, admin):
        try:
            self.__cur.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                               (telegram_id, username, balance, admin))
            self.__db.commit()
        except Exception as e:
            print('Ошибка добавления в БД', e)
            return False
        return True

    def update_balance(self, balance, **kwargs):
        try:
            balance = str(balance)
            items = list(kwargs.items())[0]
            promt = f"UPDATE users SET balance = '{balance}' WHERE {items[0]} = '{items[1]}'"
            # print(promt)
            self.__cur.execute(promt)
            self.__db.commit()
        except Exception as e:
            print('Ошибка изменения в БД', e)
            return False
        return True

    def get_user(self, **kwargs):  # <-- id=02
        try:
            items = list(kwargs.items())[0]
            self.__cur.execute(f"SELECT * FROM users WHERE {items[0]} = '{items[1]}'")
            return self.__cur.fetchall()
        except Exception as e:
            print('Ошибка получения члена из БД', e)
            return False

    def f(self):
        try:
            self.__cur.execute(f"UPDATE users SET admin = '1' WHERE username = 'DanielBobrov'")
            self.__db.commit()
            return self.__cur.fetchall()
        except Exception as e:
            print('Ошибка получения члена из БД', e)
            return False


if __name__ == "__main__":
    db = DataBase()
    print(db)
    db.f()
    print(db)