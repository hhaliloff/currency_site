import sqlite3

class DatabaseController():
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""CREATE TABLE currency(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        num_code TEXT,
        char_code TEXT,
        name TEXT,
        value REAL,
        nominal INTEGER
        )
        """)

        self.cursor.execute("""CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT,
        name TEXT,
        password TEXT
        )
        """)

        self.cursor.execute("""CREATE TABLE subscription
                               (
                                   id       INTEGER PRIMARY KEY AUTOINCREMENT,
                                   login    TEXT,
                                   valute     TEXT
                               )
                            """)


    def create_currency(self, num_code, char_code, name, value, nominal):
        self.cursor.execute("INSERT INTO currency (num_code, char_code, name, value, nominal) VALUES (?, ?, ?, ?, ?)",
                            (num_code, char_code, name, value, nominal))
        self.conn.commit()

    def read_currency(self):
        self.cursor.execute("SELECT * FROM currency")
        return self.cursor.fetchall()

    def update_currency(self, currency_id, num_code, char_code, name, value, nominal):
        self.cursor.execute("UPDATE currency SET num_code = ?, char_code = ?, name = ?, value = ?, nominal = ? WHERE id = ?",
                            (num_code, char_code, name, value, nominal, currency_id))
        self.conn.commit()

    def delete_currency(self, currency_id):
        self.cursor.execute("DELETE FROM currency WHERE id = ?", (currency_id,))
        self.conn.commit()

    def create_user(self, login, name, password):
        self.cursor.execute("INSERT INTO user (login, name, password) VALUES (?, ?, ?)",
                            (login, name, password))
        self.conn.commit()

    def read_user(self):
        self.cursor.execute("SELECT * FROM user")
        return self.cursor.fetchall()

    def delete_user(self, login):
        self.cursor.execute("DELETE FROM user WHERE login = ?", (login,))
        self.conn.commit()

    def create_subscription(self, login, valute):
        self.cursor.execute("INSERT INTO subscription (login, valute) VALUES (?, ?)",
                            (login, valute))
        self.conn.commit()

    def read_subscription(self):
        self.cursor.execute("SELECT * FROM subscription")
        return self.cursor.fetchall()

    def delete_subscription(self, login, valute):
        self.cursor.execute("DELETE FROM subscription WHERE login = ? AND valute = ?", (login, valute))
        self.conn.commit()

    def currency_by_char_code(self, char_code):
        self.cursor.execute("SELECT value FROM currency WHERE char_code = ?", (char_code,))
        return self.cursor.fetchone()

    def subs_by_login(self, login):
        self.cursor.execute("SELECT valute FROM subscription WHERE login = ?", (login,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_user_by_login(self, login):
        self.cursor.execute("SELECT * FROM user WHERE login = ?", (login,))
        return self.cursor.fetchone()
