import time
from concurrent.futures.thread import ThreadPoolExecutor

from arbitrager.arbitrager import Arbitrager
from bot.bot import BetAssistantBot
from constants import SPORT_SHORT_NAMES_TO_FULL


class Scheduler:
    TIMEOUT = 2 * 60 * 60  # 2 hours

    def __init__(self, bot: BetAssistantBot, sport_names: list):
        self.bot = bot
        self.sport_names = sport_names

    def __update_on_timeout(self):
        while True:
            for sport_name in self.sport_names:
                arbitrager = Arbitrager(sport_name)
                self.bot.notify_subscribers(arbitrager.sport_name)
            time.sleep(Scheduler.TIMEOUT)

    def run(self):
        with ThreadPoolExecutor() as executor:
            executor.submit(self.__update_on_timeout)
            executor.submit(self.bot.polling(none_stop=True))


if __name__ == '__main__':
    bot = BetAssistantBot()
    scheduler = Scheduler(bot, list(SPORT_SHORT_NAMES_TO_FULL.keys()))
    scheduler.run()
