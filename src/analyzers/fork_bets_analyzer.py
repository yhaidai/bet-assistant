from pprint import pprint

from analyzers.analyzer import Analyzer
from grouper import Grouper


class ForkBetsAnalyzer(Analyzer):
    """
    Class for analyzing betting info and finding possible fork bets
    """
    def __init__(self, sport_type):
        super().__init__(sport_type)

    def get_fork_bets(self):
        """
        Get all profitable fork bets

        :return: all profitable fork bets in the form:
        bets[match_title][bet_title_1 | bet_title_2 | ... | bet_title_n][profit_str] = {odds: bookmaker}
        :rtype: dict
        """
        fork_bets = {}
        grouped_bets = Grouper.group(self.all_bets)

        for match_title in grouped_bets:
            for group_title in grouped_bets[match_title]:
                best_odds_bets = {}
                for bet_title, odds in grouped_bets[match_title][group_title].items():
                    max_odds_value = max(odds.keys())
                    best_odds_bets[bet_title] = {max_odds_value: odds[max_odds_value]}

                max_odds_values = []
                for max_odds in best_odds_bets.values():
                    max_odds_values += max_odds.keys()
                profit = self._get_fork_profit(max_odds_values)
                bet_amounts = self._get_fork_bet_amounts(max_odds_values)

                # add fork bet
                if profit > 0:
                    fork_bets.setdefault(match_title, {})
                    fork_bet_title = self._compile_fork_bet_title(list(best_odds_bets.keys()))
                    text = self._compile_fork_text_dict(list(best_odds_bets.values()), bet_amounts, profit)
                    fork_bets[match_title][fork_bet_title] = text

        return fork_bets

    @staticmethod
    def _compile_fork_bet_title(bet_titles):
        """
        Compiles fork bet title from two bet titles

        :param bet_titles: bet titles to compile the fork bet title from
        :type bet_titles: list
        :return: compiled fork bet title in the form: bet_title_1 | bet_title_2 | ... | bet_title_n
        :rtype: str
        """
        bet_titles.sort()
        result = ''
        for bet_title in bet_titles:
            result += bet_title + ' | '

        return result[:-3]

    @staticmethod
    def _compile_fork_text_dict(odds, bet_amounts, profit):
        """
        Compiles fork bet result dictionary from given odds, bookmaker names and profit

        :param odds: odds list in the form [{odds_value: bookmaker_name},...]
        :type odds: list
        :param profit: average profit from this fork bet
        :type profit: float
        :return: fork bet result dict in the form:
        {profit: max_odds(bookmaker1) - max_opposite_odds(bookmaker2)}
        :rtype: dict
        """
        key = '*Profit - ' + str('{:.2f}'.format(profit * 100)) + '%*'
        value = {}
        for odds_dict in odds:
            for odds_value, bookmaker in odds_dict.items():
                value.update({'*' + odds_value + '(' + bet_amounts[odds_value] + ')*': bookmaker})

        return {key: value}

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
        bet_amounts = {o: 'Bet amount: ' + str('{:.4f}'.format(1 / float(o) / reciprocals_sum)) for o in odds}
        return bet_amounts


if __name__ == '__main__':
    analyzer = ForkBetsAnalyzer('csgo')
    b = analyzer.get_fork_bets()
    pprint(b)
