from telebot import TeleBot
from secrets import token


class Bot(TeleBot):
    def __init__(self):
        super().__init__(token)
        self.polling(none_stop=True)
