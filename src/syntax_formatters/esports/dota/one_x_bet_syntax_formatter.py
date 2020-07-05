from pprint import pprint, pformat
import os.path

from dota.abstract_syntax_formatter import AbstractSyntaxFormatter
from esports.one_x_bet_syntax_formatter import OneXBetSyntaxFormatter as OSF
from sample_data.dota import one_x_bet


class OneXBetSyntaxFormatter(AbstractSyntaxFormatter, OSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the 1xbet website
    """
    pass


if __name__ == '__main__':
    formatter = OneXBetSyntaxFormatter()
    formatter.apply_unified_syntax_formatting(one_x_bet.bets)
    pprint(formatter.bets)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\one_x_bet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('bets =', pformat(formatter.bets), file=f)
