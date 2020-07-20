import os

from analyzers.best_odds_analyzer import BestOddsAnalyzer
from constants import sport_name
from groupers.football.football_fork_grouper import FootballForkGrouper
from groupers.esports.csgo.csgo_fork_grouper import CSGOForkGrouper
from groupers.esports.dota.dota_fork_grouper import DotaForkGrouper
from groupers.esports.lol.lol_fork_grouper import LoLForkGrouper


class ForkBetsAnalyzer(BestOddsAnalyzer):
    """
    Class for analyzing betting info and finding possible fork bets
    """
    _PROFIT_THRESHOLD = 10
    _GROUPERS = {
        'csgo': CSGOForkGrouper(),
        'dota': DotaForkGrouper(),
        'lol': LoLForkGrouper(),
        'football': FootballForkGrouper(),
    }

    def __init__(self, sport_type):
        super().__init__(sport_type)
        self._fork_grouper = self._GROUPERS[sport_type]

    def get_fork_bets_sport(self):
        """
        Get all profitable fork bets

        :return: all profitable fork bets in the form:
        bets[match_title][bet_title_1 | bet_title_2 | ... | bet_title_n][profit_str] = {odds: bookmaker}
        :rtype: dict
        """
        best_odds_bets_sport = self.get_best_odds_bets_sport()
        fork_bets_sport = self._fork_grouper.group_bets(best_odds_bets_sport)

        for match in list(fork_bets_sport):
            for bet_group in list(match):
                if len(bet_group) == 1:
                    match.bets.remove(bet_group)
                    continue

                odds = bet_group.get_odds()
                try:
                    profit = self._get_fork_profit(odds)
                except ValueError:
                    match.bets.remove(bet_group)
                    continue

                # add fork bet
                if not 0 < profit < self._PROFIT_THRESHOLD:
                    match.bets.remove(bet_group)
                else:
                    bet_group.title += '(*Profit - ' + str('{:.2f}'.format(profit * 100)) + '%*)'
                    bet_amounts = self._get_fork_bet_amounts(odds)
                    for bet in bet_group:
                        bet.odds += bet_amounts[bet.odds]

            if not match.bets:
                fork_bets_sport.matches.remove(match)

        return fork_bets_sport

    @staticmethod
    def _get_fork_profit(odds):
        """
        Calculates average profit of betting on odds1 and odds2 simultaneously,
        assuming that if first bet wins, second loses and vice versa

        :param odds: bets odds
        :type odds: list
        :return: max profit value
        :rtype: float
        """
        reciprocals = [1 / float(o) for o in odds]
        reciprocals_sum = sum(reciprocals)
        return 1 / reciprocals_sum - 1

    @staticmethod
    def _get_fork_bet_amounts(odds):
        reciprocals = [1 / float(o) for o in odds]
        reciprocals_sum = sum(reciprocals)
        bet_amounts = {o: '. Bet amount: ' + str('{:.4f}'.format(1 / float(o) / reciprocals_sum)) for o in odds}
        return bet_amounts


if __name__ == '__main__':
    analyzer = ForkBetsAnalyzer(sport_name)
    csgo_forks = analyzer.get_fork_bets_sport()
    print(csgo_forks)

    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\forks.py'
    with open(path, 'w', encoding='utf-8') as f:
        print(csgo_forks, file=f)
