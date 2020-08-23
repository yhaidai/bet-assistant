import os
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from datetime import datetime
from pprint import pprint

from bet_group import BetGroup
from constants import sport_name
from csgo_fork_grouper import CSGOForkGrouper
from dota_fork_grouper import DotaForkGrouper
from exceptions import RendererTimeoutException
from football_fork_grouper import FootballForkGrouper
from lol_fork_grouper import LoLForkGrouper
from match import Match
from registry import registry
from sport import Sport

# doing explicit import in order to able to unpickle scraped data
from scrapers.favorit_scraper import FavoritScraper
from scrapers.ggbet_scraper import GGBetScraper
from scrapers.marathon_scraper import MarathonScraper
from scrapers.one_x_bet_scraper import OneXBetScraper
from scrapers.parimatch_scraper import ParimatchScraper


class Arbitrager:
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
        self.sports = []
        self._fork_grouper = self._GROUPERS[sport_name]
        # for scraper, formatter in registry.items():
        #     sport = scraper.get_matches_info_sport(sport_name)
        #     self.sports.append(sport)

        self.sports = Arbitrager._get_sports_from_sample_data()

        self.all_matches_sport = self.get_all_bets_sport()
        print(self.all_matches_sport)

    @staticmethod
    def _get_sports_from_sample_data():
        sports = []
        path = os.path.abspath(os.path.dirname(__file__)).replace('arbitrager',
                                                                  'scrapers\\sample_data\\{}\\'.format(sport_name))
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

        group_id = 0
        group_count = len(match_groups)
        for title, group in match_groups.items():
            group_id += 1
            if len(group) < 2 or group[0].date_time <= datetime.now():
                continue
            print('Group', group_id, 'of', group_count, ':')
            all_bets = []

            # with ThreadPoolExecutor() as executor:
            #     futures = []
            #     for match in group:
            #         print(match.url)
            #         try:
            #             # TODO: move multiple occurrences fix to grouper
            #             if not match.bets:
            #                 future = executor.submit(match.scraper.scrape_match_bets, match)
            #                 futures.append(future)
            #             else:
            #                 print('Match has occurred in multiple groups')
            #                 continue
            #         except RendererTimeoutException:
            #             print('Caught RendererTimeoutException')
            #             continue
            #
            #     wait(futures, return_when=ALL_COMPLETED)
            #
            #     for match in group:
            #         formatter = registry[match.scraper][self.all_matches_sport.name]
            #         formatter.format_match(match)
            #         all_bets += match.bets
            #
            #     all_bets_match = Match(title, None, group[0].date_time, None, all_bets)
            #     Arbitrager.remove_anything_but_best_odds_bets(all_bets_match)
            #     self.remove_anything_but_arbitrage_bets(all_bets_match)
            #     if all_bets_match.bets:
            #         self.all_matches_sport.matches.append(all_bets_match)
            #         print(all_bets_match)
            #     print()

            for match in group:
                print(match.url)
                try:
                    # TODO: move multiple occurrences fix to grouper
                    if not match.bets:
                        match.scraper.scrape_match_bets(match)
                    else:
                        print('Match has occurred in multiple groups')
                        continue
                except RendererTimeoutException:
                    print('Caught RendererTimeoutException')
                    continue
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

            # add fork bet
            if not 0 < profit < Arbitrager._PROFIT_THRESHOLD:
                match.bets.remove(bet_group)
            else:
                highlighter = '*'
                bet_group.title += '(' + highlighter + 'Profit - ' + str('{:.2f}'.format(profit * 100)) + '%' + \
                                   highlighter + ')'
                bet_amounts = Arbitrager._get_arbitrage_bet_amounts(odds)
                for bet in bet_group:
                    bet.odds += bet_amounts[bet.odds]

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
    def _get_arbitrage_bet_amounts(odds):
        reciprocals = [1 / float(o) for o in odds]
        reciprocals_sum = sum(reciprocals)
        bet_amounts = {o: '. Bet amount: ' + str('{:.4f}'.format(1 / float(o) / reciprocals_sum)) for o in odds}
        return bet_amounts


if __name__ == '__main__':
    try:
        t = time.time()
        analyzer = Arbitrager(sport_name)
        print('Elapsed:', time.time() - t)
    finally:
        for scraper in registry:
            scraper.renderer.quit()
