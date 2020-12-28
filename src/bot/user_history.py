import mysql.connector

from secrets import *
from user import User


class UserHistory:
    __TABLE_NAME = 'users'

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    cursor = connection.cursor()
    cursor.execute(f'CREATE DATABASE IF NOT EXISTS {DB_NAME}')
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {__TABLE_NAME} (ID INTEGER PRIMARY KEY, subscriptions VARCHAR(255), 
                   last_menu_option_id INTEGER)''')

    cursor.execute(f'SELECT * FROM {__TABLE_NAME}')
    users = [User(id, eval(sub), last_menu_option_id) for id, sub, last_menu_option_id in cursor.fetchall()]
    print(users)

    @staticmethod
    def get_user(user_id):
        for user in UserHistory.users:
            if user.id == user_id:
                return user
        return None

    @staticmethod
    def add_user(user):
        if user not in UserHistory.users:
            UserHistory.users.append(user)
            UserHistory.cursor.execute(
                f'INSERT INTO {UserHistory.__TABLE_NAME} VALUES (%s, %s, %s)',
                (user.id, str(user.subscriptions), user.menu.current_option.id)
            )
            UserHistory.connection.commit()

    @staticmethod
    def update_user(user):
        if user in UserHistory.users:
            UserHistory.cursor.execute(
                f'''UPDATE {UserHistory.__TABLE_NAME} 
                SET subscriptions = %s, last_menu_option_id = %s
                WHERE ID = %s''',
                (str(user.subscriptions), user.menu.current_option.id, user.id)
            )
            UserHistory.connection.commit()
