import sqlite3
from config import DATABASE
import logging
import io
import csv
from datetime import datetime
import sys


class Database:
    def __init__(self):
        try:
            self.conn = sqlite3.connect(DATABASE)
            self.cursor = self.conn.cursor()
            self.create_database()
            logging.info('Database succesfully connected.')
        except Exception as e:
            logging.fatal('Database initializing error!')
            logging.error('Error message: ' + str(e))
            sys.exit(-1)

    def create_database(self):
        logging.info('Trying to create database.')
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS users ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
            'user_id INTEGER UNIQUE NOT NULL, '
            'user_name TEXT NOT NULL, '
            'user_surname TEXT,'
            'user_nickname TEXT)'
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS transactions ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
            'user_id INTEGER NOT NULL, '
            'type TEXT NOT NULL, '
            'value REAL NOT NULL, '
            'name TEXT NOT NULL, '
            'category TEXT NOT NULL, '
            'time REAL NOT NULL)'
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS settings ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
            'user_id INTEGER UNIQUE NOT NULL, '
            'currency TEXT NOT NULL, '
            'sp1 TEXT NOT NULL, '
            'sp2 TEXT NOT NULL, '
            'sp3 TEXT NOT NULL, '
            'pr1 TEXT NOT NULL, '
            'pr2 TEXT NOT NULL, '
            'pr3 TEXT NOT NULL)'
        )
        self.conn.commit()

    def check_user(self, user):
        self.cursor.execute(
            'SELECT id FROM users WHERE user_id = ?',
            (user.id,)
        )
        logging.info(f'check_user() has been called by ID: {user.id}')
        return self.cursor.fetchone() is not None

    def create_user(self, user):
        self.cursor.execute(
            'INSERT INTO users (user_id, user_name, user_surname, user_nickname) VALUES (?, ?, ?, ?)',
            (user.id, user.first_name, user.last_name, user.username)
        )
        self.cursor.execute(
            'INSERT INTO settings (user_id, currency, sp1, sp2, sp3, pr1, pr2, pr3) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (user.id, 'грн', 'Еда', 'Транспорт', 'Равзлечения', 'Зарплата', 'Пособие', 'Подработка')
        )
        self.conn.commit()
        logging.info(f'create_user() has been called by ID: {user.id}')

    def add_transaction(self, data, user):
        self.cursor.execute(
            'INSERT INTO transactions (user_id, type, value, name, category, time) VALUES (?, ?, ?, ?, ?, ?)',
            (user.id, data['type'], data['value'], data['name'], data['category'], data['time'])
        )
        self.conn.commit()
        logging.info(f'Transaction (type: {data["type"]}) has been added by ID: {user.id}')

    def get_categories(self, user, tp):
        self.cursor.execute(
            'SELECT DISTINCT category FROM transactions WHERE user_id = ? and type = ?',
            (user.id, tp)
        )
        result = self.cursor.fetchall()
        logging.info(f'get_categories() has been called by ID: {user.id}')
        if len(result) != 0:
            return [x[0] for x in result]
        else:
            return None

    def get_limits(self, user):
        self.cursor.execute(
            'SELECT MIN(time) FROM transactions WHERE user_id = ?',
            (user.id,)
        )
        first = self.cursor.fetchone()
        logging.info(f'get_limits() has been called by ID: {user.id}')
        if first is not None:
            first = first[0]
            self.cursor.execute(
                'SELECT MAX(time) FROM transactions WHERE user_id = ?',
                (user.id,)
            )
            last = self.cursor.fetchone()[0]
            return [first, last]
        return None

    def get_sum(self, user, tp, limits):
        self.cursor.execute(
            'SELECT SUM(value) FROM transactions WHERE user_id = ? and type = ? and time >= ? and time <= ?',
            (user.id, tp, limits[0], limits[1])
        )
        result = self.cursor.fetchone()[0]
        logging.info(f'get_sum() has been called by ID: {user.id}')
        if result is not None:
            return result
        else:
            return 0

    def get_categories_bydate(self, user, tp, limits):
        self.cursor.execute(
            'SELECT DISTINCT category FROM transactions WHERE user_id = ? and type = ? and time >= ? and time <= ?',
            (user.id, tp, limits[0], limits[1])
        )
        result = self.cursor.fetchall()
        logging.info(f'get_categories_bydate() has been called by ID: {user.id}')
        if len(result) != 0:
            return [x[0] for x in result]
        else:
            return None

    def get_sum_bycategory(self, user, tp, limits, category):
        self.cursor.execute(
            'SELECT SUM(value) FROM transactions WHERE user_id = ? and type = ? and time >= ? and time <= ? '
            'and category = ?',
            (user.id, tp, limits[0], limits[1], category)
        )
        result = self.cursor.fetchone()[0]
        logging.info(f'get_sum_bycategory() has been called by ID: {user.id}')
        if result is not None:
            return result
        else:
            return 0

    def get_all_transactions(self, user):
        self.cursor.execute(
            'SELECT id, strftime("%d.%m.%Y", time, "unixepoch"), type, category, name, value '
            'FROM transactions WHERE user_id = ?',
            (user.id,)
        )
        result = self.cursor.fetchall()
        logging.info(f'get_all_transactions() has been called by ID: {user.id}')
        csv_data = io.StringIO()
        writer = csv.writer(csv_data)
        writer.writerow(['ID транзакции', 'Дата', 'Тип', 'Категория', 'Описание', 'Сумма'])
        for row in result:
            writer.writerow(row)
        csv_data.seek(0)
        return csv_data

    def check_id(self, user, transaction_id):
        self.cursor.execute(
            'SELECT name FROM transactions WHERE user_id = ? and id = ?',
            (user.id, int(transaction_id))
        )
        result = self.cursor.fetchone()
        logging.info(f'check_id() has been called by ID: {user.id}')
        return result is not None

    def get_transaction(self, user, transaction_id):
        self.cursor.execute(
            'SELECT type, value, name, category, strftime("%d.%m.%Y %H:%M", time, "unixepoch") '
            'FROM transactions WHERE id = ?',
            (int(transaction_id),)
        )
        logging.info(f'get_transaction() has been called by ID: {user.id}')
        return self.cursor.fetchone()

    def update_transaction(self, user, data):
        time = datetime.strptime(data['date'], '%d.%m.%Y %H:%M').timestamp()
        self.cursor.execute(
            'UPDATE transactions SET value = ?, name = ?, category = ?, time = ? '
            'WHERE id = ?',
            (data['value'], data['name'], data['category'], time, data['transaction_id'])
        )
        self.conn.commit()
        logging.info(f'update_transaction() has been called by ID: {user.id}')

    def delete_transaction(self, user, transaction_id):
        self.cursor.execute(
            'DELETE FROM transactions WHERE id = ?',
            (transaction_id,)
        )
        self.conn.commit()
        logging.info(f'delete_transaction() has been called by ID: {user.id}')

    def get_settings(self, user):
        self.cursor.execute(
            'SELECT currency, sp1, sp2, sp3, pr1, pr2, pr3 '
            'FROM settings WHERE user_id = ?',
            (user.id,)
        )
        result = self.cursor.fetchone()
        settings = {
            'currency': result[0],
            'sp1': result[1],
            'sp2': result[2],
            'sp3': result[3],
            'pr1': result[4],
            'pr2': result[5],
            'pr3': result[6]
        }
        logging.info(f'get_settings() has been called by ID: {user.id}')
        return settings

    def update_categories(self, user, categories):
        self.cursor.execute(
            'UPDATE settings SET sp1 = ?, sp2 = ?, sp3 = ?, pr1 = ?, pr2 = ?, pr3 = ? '
            'WHERE user_id = ?',
            (categories[0], categories[1], categories[2], categories[3], categories[4], categories[5], user.id)
        )
        self.conn.commit()
        logging.info(f'update_categories() has been called by ID: {user.id}')
