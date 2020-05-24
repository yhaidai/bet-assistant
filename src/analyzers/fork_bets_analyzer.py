from analyzers.analyzer import Analyzer
from syntax_formatter import SyntaxFormatter


class ForkBetsAnalyzer(Analyzer):
    """
    Class for analyzing betting info and finding possible fork bets
    """
    oppositions = {
        ' over ': ' under ',
        ' +': ' -',
        ' even': ' odd'
        }
    ignore_markers = ['exactly']

    def __init__(self, sport_type):
        super().__init__(sport_type)

    def get_fork_bets(self):
        fork_bets = {}

        for match_title in self.all_bets.keys():
            for bet_title, odds in self.all_bets[match_title].items():
                if self._ignore(bet_title):
                    continue

                opposite_bet_title = self._get_opposite_bet_title(match_title, bet_title)
                if opposite_bet_title not in self.all_bets[match_title]:
                    continue
                opposite_odds = self.all_bets[match_title][opposite_bet_title]

                max_odds = max(odds.keys())
                max_opposite_odds = max(opposite_odds.keys())
                try:
                    profit = self._get_fork_profit(float(max_odds), float(max_opposite_odds))
                except ValueError:
                    print(match_title)
                    print(bet_title)
                    print(opposite_bet_title)
                    print(max_odds + ' ' + max_opposite_odds + '\n')

                # add fork bet
                if profit > 0:
                    fork_bets.setdefault(match_title, {})
                    fork_bet_title = self._compile_fork_bet_title(bet_title, opposite_bet_title)
                    text = self._compile_fork_text_dict(max_odds, max_opposite_odds, odds[max_odds],
                                                   opposite_odds[max_opposite_odds], profit)
                    fork_bets[match_title][fork_bet_title] = text

        return fork_bets

    def _get_opposite_bet_title(self, match_title, bet_title):
        oppositions = {}
        for k, v in self.oppositions.items():
            if k in bet_title:
                oppositions[k] = v
            if v in bet_title:
                oppositions[v] = k

        teams = SyntaxFormatter.decompile_match_title(match_title)
        if teams[0] in bet_title:
            oppositions[teams[0]] = teams[1]
        if teams[1] in bet_title:
            oppositions[teams[1]] = teams[0]

        opposite_bet_title = None
        if oppositions:
            opposite_bet_title = bet_title
            for entity, opposition in oppositions.items():
                opposite_bet_title = opposite_bet_title.replace(entity, opposition)

        # print(bet_title + ' - ' + str(opposite_bet_title))
        return opposite_bet_title

    @staticmethod
    def _ignore(bet_title):
        for marker in ForkBetsAnalyzer.ignore_markers:
            if marker in bet_title:
                return True

        return False

    @staticmethod
    def _compile_fork_bet_title(bet_title1, bet_title2):
        bet_titles = [bet_title1, bet_title2]
        bet_titles.sort()
        return bet_titles[0] + ' | ' + bet_titles[1]

    @staticmethod
    def _compile_fork_text_dict(max_odds, max_opposite_odds, bookmaker1, bookmaker2, profit):
        key = '*Profit - ' + str('{:.2f}'.format(profit * 100)) + '%'
        value = max_odds + '*(' + bookmaker1 + ') - *' + max_opposite_odds + '*(' + bookmaker2 + ')'
        return {key: value}

    @staticmethod
    def _get_fork_profit(odds, opposite_odds):
        """
        Calculates max profit of betting on odds1 and odds2 simultaneously,
        assuming that if first bet wins, second loses and vice versa

        :param odds: bet odds
        :type odds: float
        :param opposite_odds: opposite bet odds
        :type opposite_odds: float
        :return: max profit value
        :rtype: float
        """
        odds_sum = odds + opposite_odds
        return (odds * opposite_odds - odds_sum) / odds_sum
