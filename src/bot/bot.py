from secrets import token

from telebot import TeleBot


class Bot(TeleBot):
    def __init__(self):
        super().__init__(token)
        self.polling(none_stop=True)
