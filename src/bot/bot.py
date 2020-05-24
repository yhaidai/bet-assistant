import time
from json import dumps

from telebot import TeleBot
from telebot.apihelper import ApiException

from analyzers.analyzer import Analyzer
from analyzers.best_odds_analyzer import BestOddsAnalyzer
from analyzers.fork_bets_analyzer import ForkBetsAnalyzer
from one_x_bet_scraper import OneXBetScraper
from parimatch_scraper import ParimatchScraper
from secrets import token
from util import bets_to_json_strings


class BetAssistantBot(TeleBot):
    message_max_length = 4096

    def __init__(self):
        super().__init__(token)
        self.scrapers = [ParimatchScraper(), OneXBetScraper()]
        self.bets_list = []
        self._init_commands()

    def send_long_messages(self, chat_id, strings, reply_to, parse_mode='Markdown'):
        c = 0
        for string in strings:
            while len(string) > 0:
                length = BetAssistantBot.message_max_length
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
            self.send_message(message.chat.id, dumps('–  -'))

        @self.message_handler(commands=['prematch_csgo_analytics'])
        def command_start_handler(message):
            analyzer = BestOddsAnalyzer('csgo')
            best_odds_bets = analyzer.get_best_odds_bets()
            json_strings = bets_to_json_strings(best_odds_bets)
            self.send_long_messages(message.chat.id, json_strings, message.message_id)

        @self.message_handler(commands=['prematch_csgo_forks'])
        def command_start_handler(message):
            analyzer = ForkBetsAnalyzer('csgo')
            fork_bets = analyzer.get_fork_bets()
            json_strings = bets_to_json_strings(fork_bets)
            self.send_long_messages(message.chat.id, json_strings, message.message_id)


if __name__ == '__main__':
    bot = BetAssistantBot()
    bot.polling(none_stop=True)
