import time
from json import dumps
from pprint import pprint

from telebot import TeleBot
from telebot.apihelper import ApiException

from one_x_bet_scraper import OneXBetScraper
from parimatch_scraper import ParimatchScraper
from secrets import token
from syntax_formatters.sample_data import parimatch, one_x_bet


class Bot(TeleBot):
    message_max_length = 4096

    def __init__(self):
        super().__init__(token)
        self.scrapers = [ParimatchScraper(), OneXBetScraper()]
        self.bets_list = []
        self._init_commands()

    def _init_commands(self):
        @self.message_handler(commands=['start', 'help'])
        def command_start_handler(message):
            self.send_message(message.chat.id, dumps('–  -'))

        @self.message_handler(commands=['prematch_csgo_analytics'])
        def command_start_handler(message):
            result = {}
            for scraper in self.scrapers:
                bets = scraper.get_bets('csgo')
                self.bets_list.append(bets)

            # self.bets_list.append(one_x_bet.bets)
            # self.bets_list.append(parimatch.bets)

            all_bets = {}
            for bets in self.bets_list:
                for match_title in bets.keys():
                    all_bets.setdefault(match_title, {})
                    for bet_title, odds in bets[match_title].items():
                        all_bets[match_title].setdefault(bet_title, []).append(odds)

            for match_title in all_bets.keys():
                result[match_title] = {}
                for bet_title, odds in all_bets[match_title].items():
                    best_odds = max(odds)
                    result[match_title][bet_title] = {'*Max - ' + best_odds + '*': odds}

            c = 0
            for match_title in result.keys():
                json_str = dumps(result[match_title], indent=4) + '\n\n'
                # print(len(json_str))
                while len(json_str) > 0:
                    length = Bot.message_max_length
                    while True:
                        try:
                            self.send_message(message.chat.id, json_str[:length], parse_mode='Markdown')
                            c += 1
                            break
                        except ApiException:
                            length -= 10
                    json_str = json_str[Bot.message_max_length:]
                    if c % 100 == 0:
                        time.sleep(300)


if __name__ == '__main__':
    bot = Bot()
    bot.polling(none_stop=True)
