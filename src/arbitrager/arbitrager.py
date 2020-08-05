from pprint import pprint

from bet_group import BetGroup
from constants import sport_name
from csgo_fork_grouper import CSGOForkGrouper
from dota_fork_grouper import DotaForkGrouper
from football_fork_grouper import FootballForkGrouper
from lol_fork_grouper import LoLForkGrouper
from match import Match
from registry import registry
from sport import Sport
from fork_grouper import ForkGrouper
from syntax_formatters.esports.csgo.sample_data import favorit, parimatch, one_x_bet, ggbet, marathon
# from syntax_formatters.esports.dota.sample_data import favorit, parimatch, one_x_bet, ggbet, marathon
# from syntax_formatters.esports.lol.sample_data import favorit, parimatch, one_x_bet, ggbet, marathon
# from syntax_formatters.football.sample_data import favorit, parimatch, one_x_bet, ggbet, marathon


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
        for scraper, formatter in registry.items():
            sport = scraper.get_matches_info_sport(sport_name)
            self.sports.append(sport)
        # self.sports = [
        #     Sport.from_dict(one_x_bet.sport),
        #     Sport.from_dict(parimatch.sport),
        #     Sport.from_dict(marathon.sport),
        #     Sport.from_dict(ggbet.sport),
        #     Sport.from_dict(favorit.sport),
        #     ]

        self.all_matches_sport = self.get_all_bets_sport()
        print(self.all_matches_sport)

    def get_all_bets_sport(self) -> Sport:
        all_matches = []
        for sport in self.sports:
            all_matches += sport.matches
        self.all_matches_sport = Sport(self.sports[0].name, all_matches)
        self._scrape_bets()

        return self.all_matches_sport

    def _scrape_bets(self):
        # print(self.all_matches_sport, '\n' * 6)
        match_groups = self._fork_grouper.get_match_groups(self.all_matches_sport)
        pprint(match_groups)
        for title, group in match_groups.items():
            if len(group) < 2:
                for match in group:
                    self.all_matches_sport.matches.remove(match)
                continue

            all_bets = []
            for match in group:
                print(match.url)
                match.scraper.scrape_match_bets(match)
                # print(match)
                all_bets += match.bets
                formatter = registry[match.scraper][self.all_matches_sport.name]
                formatter.format_match(match)
                try:
                    self.all_matches_sport.matches.remove(match)
                except ValueError:
                    print('Same match occurred in multiple groups!')

            all_bets_match = Match(title, '', group[0].date_time, None, all_bets)
            self.all_matches_sport.matches.append(all_bets_match)
            Arbitrager.remove_anything_but_best_odds_bets(all_bets_match)
            self.remove_anything_but_arbitrage_bets(all_bets_match)
            if len(all_bets_match.bets) > 0:
                print(all_bets_match)

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
            # if False:
            if not 0 < profit < Arbitrager._PROFIT_THRESHOLD:
                match.bets.remove(bet_group)
            else:
                bet_group.title += '(*Profit - ' + str('{:.2f}'.format(profit * 100)) + '%*)'
                bet_amounts = Arbitrager._get_arbitrage_bet_amounts(odds)
                for bet in bet_group:
                    bet.odds += bet_amounts[bet.odds]

        # if len(match.bets) == 0:
        #     self.all_matches_sport.matches.remove(match)

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
    analyzer = Arbitrager(sport_name)
    # s = analyzer.get_all_bets_sport()
    # print(s)
