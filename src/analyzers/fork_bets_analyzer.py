from analyzers.analyzer import Analyzer
from match_title_compiler import MatchTitleCompiler


class ForkBetsAnalyzer(Analyzer):
    """
    Class for analyzing betting info and finding possible fork bets
    """
    _OPPOSITIONS = {
        ' over ': ' under ',
        ' +': ' -',
        ' even': ' odd'
    }
    _IGNORE_MARKERS = ['exactly']
    # multiway_markers = ['draw']

    def __init__(self, sport_type):
        super().__init__(sport_type)

    def get_fork_bets(self):
        """
        Get all profitable fork bets

        :return: all profitable fork bets in the form:
        bets[match_title][bet_title | opposite_bet_title] = profit_str
        :rtype: dict
        """
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
        """
        Get opposite bet title i.e. such bet title that if
        given one wins opposite loses and vice versa

        :param match_title: title of the match which bet title belongs to
        :type match_title: str
        :param match_title: bet title to get opposite to
        :type match_title: str
        :return: opposite bet title
        :rtype: str
        """
        oppositions = {}
        for k, v in self._OPPOSITIONS.items():
            if k in bet_title:
                oppositions[k] = v
            if v in bet_title:
                oppositions[v] = k

        teams = MatchTitleCompiler.decompile_match_title(match_title)
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
        """
        Checks whether to ignore bet title based on containment of specific words(ignore markers)

        :param bet_title: bet title to check
        :type bet_title: str
        :return: True if bet title contains at least one ignore marker, False otherwise
        :rtype: bool
        """
        for marker in ForkBetsAnalyzer._IGNORE_MARKERS:
            if marker in bet_title:
                return True

        return False

    @staticmethod
    def _compile_fork_bet_title(bet_title1, bet_title2):
        """
        Compiles fork bet title from two bet titles

        :param bet_title1: first bet title
        :type bet_title1: str
        :param bet_title2: second bet title
        :type bet_title2: str
        :return: compiled fork bet title in the form: bet_title1 | bet_title2
        :rtype: str
        """
        bet_titles = [bet_title1, bet_title2]
        bet_titles.sort()
        return bet_titles[0] + ' | ' + bet_titles[1]

    @staticmethod
    def _compile_fork_text_dict(odds1, odds2, bookmaker1, bookmaker2, profit):
        """
        Compiles fork bet result dictionary from given odds, bookmaker names and profit

        :param odds1: odds for first bet title
        :type odds1: str
        :param odds2: odds for opposite bet title
        :type odds2: str
        :param bookmaker1: name of bookmaker which provides max_odds
        :type bookmaker1: str
        :param bookmaker2: name of bookmaker which provides max_opposite_odds
        :type bookmaker2: str
        :param profit: average profit from this fork bet
        :type profit: float
        :return: fork bet result dict in the form:
        {profit: max_odds(bookmaker1) - max_opposite_odds(bookmaker2)}
        :rtype: dict
        """
        key = '*Profit - ' + str('{:.2f}'.format(profit * 100)) + '%'
        value = odds1 + '*(' + bookmaker1 + ') - *' + odds2 + '*(' + bookmaker2 + ')'
        return {key: value}

    @staticmethod
    def _get_fork_profit(odds, opposite_odds):
        """
        Calculates average profit of betting on odds1 and odds2 simultaneously,
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
