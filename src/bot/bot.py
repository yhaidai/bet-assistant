import time
from json import dumps

from telebot import TeleBot
from telebot.apihelper import ApiException

import __init__
from secrets import TOKEN
from util import bets_to_json_strings

from analyzers.best_odds_analyzer import BestOddsAnalyzer
from analyzers.fork_bets_analyzer import ForkBetsAnalyzer


class BetAssistantBot(TeleBot):
    _MESSAGE_MAX_LENGTH = 4096
    _COMMANDS = {
        '/start': 'start interacting with bot',
        '/help': 'list commands and their description',
        '/prematch_csgo_analytics':  'find best odds for csgo prematch events',
        '/prematch_csgo_forks': 'find all csgo fork betting options'
    }

    def __init__(self):
        super().__init__(TOKEN)
        self._init_commands()

    def send_long_messages(self, chat_id, strings, reply_to, parse_mode='Markdown'):
        """
        Sends messages of arbitrary length

        :param chat_id: id of the chat to message to
        :type chat_id: str
        :param strings: messages to send
        :type strings: str
        :param reply_to: id of the message to reply to
        :type reply_to: str
        :param parse_mode: parse mode applied to all strings
        :type parse_mode: str
        """
        c = 0
        for string in strings:
            while len(string) > 0:
                length = BetAssistantBot._MESSAGE_MAX_LENGTH
                while True:
                    try:
                        self.send_message(chat_id, string[:length], parse_mode=parse_mode,
                                          reply_to_message_id=reply_to)
                        c += 1
                        break
                    except ApiException:
                        length -= 10
                string = string[length:]

                # timeout every 100 messages
                if c % 100 == 0:
                    time.sleep(300)

    def _init_commands(self):
        @self.message_handler(commands=['start', 'help'])
        def command_start_handler(message):
            """
            Handles /start and /help commands
            """
            self.send_message(message.chat.id, dumps(self._COMMANDS, indent=4))

        @self.message_handler(commands=['prematch_csgo_analytics'])
        def command_start_handler(message):
            """
            Handles /prematch_csgo_analytics command
            """
            analyzer = BestOddsAnalyzer('csgo')
            best_odds_bets = analyzer.get_best_odds_bets()
            json_strings = bets_to_json_strings(best_odds_bets)
            self.send_long_messages(message.chat.id, json_strings, message.message_id)

        @self.message_handler(commands=['prematch_csgo_forks'])
        def command_start_handler(message):
            """
            Handles /prematch_csgo_forks command
            """
            analyzer = ForkBetsAnalyzer('csgo')
            fork_bets = analyzer.get_fork_bets()
            json_strings = bets_to_json_strings(fork_bets)
            self.send_long_messages(message.chat.id, json_strings, message.message_id)


if __name__ == '__main__':
    bot = BetAssistantBot()
    bot.polling(none_stop=True)
