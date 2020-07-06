from pprint import pprint, pformat
import os.path

from Sport import Sport
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
    sport = Sport.from_dict(one_x_bet.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\parimatch.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
