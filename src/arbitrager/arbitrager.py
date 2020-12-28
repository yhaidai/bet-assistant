import os
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, as_completed
from datetime import datetime
from pprint import pprint

from bet_group import BetGroup
from constants import SPORT_NAME
from csgo_fork_grouper import CSGOForkGrouper
from dota_fork_grouper import DotaForkGrouper
from exceptions import RendererTimeoutException
from football_fork_grouper import FootballForkGrouper
from lol_fork_grouper import LoLForkGrouper
from match import Match
from registry import registry
from singleton import SportNameBasedSingleton
from sport import Sport

# doing explicit import in order to able to unpickle scraped data
from scrapers.favorit_scraper import FavoritScraper
from scrapers.ggbet_scraper import GGBetScraper
from scrapers.marathon_scraper import MarathonScraper
from scrapers.one_x_bet_scraper import OneXBetScraper
from scrapers.parimatch_scraper import ParimatchScraper


class Arbitrager(metaclass=SportNameBasedSingleton):
    """
    Class for collecting betting info and analyzing it
    """
    _PROFIT_THRESHOLD = 10
    _GROUPERS = {
        'csgo': CSGOForkGrouper(),
        'dota': DotaForkGrouper(),
        'lol': LoLForkGrouper(),
        'football': FootballForkGrouper(),
        }

    def __init__(self, sport_name: str):
        """
        Scrape betting info on a given sport type

        :param sport_name: sport name e.g. 'csgo', 'dota'
        :type sport_name: str
        """
        self.sport_name = sport_name
        self.sports = []
        self._fork_grouper = self._GROUPERS[sport_name]
        self.all_matches_sport = None
        self.update()

    def update(self):
        # t = time.time()

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(scraper.get_matches_info_sport, self.sport_name) for scraper in registry]
            for future in as_completed(futures):
                self.sports.append(future.result())

        # for scraper, formatter in registry.items():
        #     sport = scraper.get_matches_info_sport(sport_name)
        #     self.sports.append(sport)

        # print('Retrieved matches info in:', time.time() - t)

        # self.sports = self._get_sports_from_sample_data()

        self.all_matches_sport = self.get_all_bets_sport()
        print(self.all_matches_sport)
        path = f'{os.path.abspath(os.path.dirname(__file__))}\\sample_data\\{self.sport_name}'
        self.all_matches_sport.write_xlsx(f'{path}.xlsx')

    def _get_sports_from_sample_data(self):
        sports = []
        path = os.path.abspath(os.path.dirname(__file__)).replace('arbitrager',
                                                                  'scrapers\\sample_data\\{}\\'.format(self.sport_name))
        for scraper in registry:
            sports.append(Sport.deserialize(path + scraper.get_name()))

        return sports

    def get_all_bets_sport(self) -> Sport:
        all_matches = []
        for sport in self.sports:
            all_matches += sport.matches
        self.all_matches_sport = Sport(self.sports[0].name, all_matches)
        self._scrape_bets()

        return self.all_matches_sport

    def _scrape_bets(self):
        match_groups = self._fork_grouper.get_match_groups(self.all_matches_sport)
        self.all_matches_sport.matches = []
        pprint(match_groups)

        # print group counts
        group_counts = [0 for scraper in registry]
        for group in match_groups.values():
            group_counts[len(group) - 1] += 1
        for group_count in group_counts:
            print(group_count, 'groups of length', group_counts.index(group_count) + 1)
        multiple_matches_groups_count = sum(group_counts[1:])
        print('2+ length groups count:', multiple_matches_groups_count)

        group_id = 0
        for title, group in list(match_groups.items()):
            if group_id == 100:
                break
            if len(group) < 2 or group[0].date_time <= datetime.now():
                continue
            group_id += 1
            print('Group', group_id, 'of', multiple_matches_groups_count, ':')
            all_bets = []

            with ThreadPoolExecutor() as executor:
                futures = []
                for match in group:
                    print(match.url)
                    try:
                        # TODO: move multiple occurrences fix to grouper
                        if not match.bets:
                            future = executor.submit(match.scraper.scrape_match_bets, match)
                            futures.append(future)
                        else:
                            print('Match has occurred in multiple groups')
                            continue
                    except RendererTimeoutException:
                        print('Caught RendererTimeoutException')
                        continue

                wait(futures, return_when=ALL_COMPLETED)

                for match in group:
                    formatter = registry[match.scraper][self.all_matches_sport.name]
                    formatter.format_match(match)
                    all_bets += match.bets

                all_bets_match = Match(title, None, group[0].date_time, None, all_bets)
                Arbitrager.remove_anything_but_best_odds_bets(all_bets_match)
                self.remove_anything_but_arbitrage_bets(all_bets_match)
                if all_bets_match.bets:
                    self.all_matches_sport.matches.append(all_bets_match)
                    print(all_bets_match)
                print()

            # for match in group:
            #     print(match.url)
            #     try:
            #         # TODO: move multiple occurrences fix to grouper
            #         if not match.bets:
            #             match.scraper.scrape_match_bets(match)
            #         else:
            #             print('Match has occurred in multiple groups')
            #             continue
            #     except RendererTimeoutException:
            #         print('Caught RendererTimeoutException')
            #         continue
            #     formatter = registry[match.scraper][self.all_matches_sport.name]
            #     formatter.format_match(match)
            #     all_bets += match.bets
            #
            # all_bets_match = Match(title, None, group[0].date_time, None, all_bets)
            # Arbitrager.remove_anything_but_best_odds_bets(all_bets_match)
            # self.remove_anything_but_arbitrage_bets(all_bets_match)
            # if all_bets_match.bets:
            #     self.all_matches_sport.matches.append(all_bets_match)
            #     print(all_bets_match)
            # print()

    @staticmethod
    def remove_anything_but_best_odds_bets(match) -> None:
        group = {}
        for bet in match:
            group.setdefault(bet.title, BetGroup(bet.title)).append(bet)
        for bet in list(match):
            if bet is not max(group[bet.title].bets):
                match.bets.remove(bet)

    def remove_anything_but_arbitrage_bets(self, match) -> None:
        self._fork_grouper.group_bets(match)
        for bet_group in list(match):
            if len(bet_group) == 1:
                match.bets.remove(bet_group)
                continue

            odds = bet_group.get_odds()
            try:
                profit = Arbitrager._get_arbitrage_profit(odds)
            except ValueError:
                print('Invalid odds value:', odds)
                match.bets.remove(bet_group)
                continue

            # add arbitrage bet
            if not 0 < profit < Arbitrager._PROFIT_THRESHOLD:
                match.bets.remove(bet_group)
            else:
                bet_group.profit = str('{:.2f}'.format(profit * 100)) + '%'
                for bet in bet_group:
                    bet.amount = Arbitrager._get_arbitrage_bet_amount(odds, bet.odds)

    @staticmethod
    def _get_arbitrage_profit(odds):
        """
        Calculates average profit of an arbitrage bet

        :param odds: odds of bets
        :type odds: list
        :return: average profit value
        :rtype: float
        """
        reciprocals = [1 / float(o) for o in odds]
        reciprocals_sum = sum(reciprocals)
        return 1 / reciprocals_sum - 1

    @staticmethod
    def _get_arbitrage_bet_amount(odds, bet_odds):
        reciprocals = [1 / float(o) for o in odds]
        reciprocals_sum = sum(reciprocals)
        return str('{:.4f}'.format(1 / float(bet_odds) / reciprocals_sum))


if __name__ == '__main__':
    try:
        t = time.time()
        arbitrager = Arbitrager(SPORT_NAME)
        print('Elapsed:', time.time() - t)
        # path = f'{os.path.abspath(os.path.dirname(__file__))}\\sample_data\\{sport_name}'
        # arbitrager.all_matches_sport.serialize(path)
        # arbitrager.all_matches_sport.write_xlsx(f'{path}.xlsx')
    finally:
        for scraper in registry:
            scraper.renderer.quit()
