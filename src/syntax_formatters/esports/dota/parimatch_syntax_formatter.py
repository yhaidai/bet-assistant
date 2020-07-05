from pprint import pprint, pformat
import os.path
from dota.abstract_syntax_formatter import AbstractSyntaxFormatter
from esports.parimatch_syntax_formatter import ParimatchSyntaxFormatter as PSF
from sample_data.dota import parimatch


class ParimatchSyntaxFormatter(AbstractSyntaxFormatter, PSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the parimatch website
    """


if __name__ == '__main__':
    formatter = ParimatchSyntaxFormatter()
    formatter.apply_unified_syntax_formatting(parimatch.bets)
    pprint(formatter.bets)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\parimatch.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('bets =', pformat(formatter.bets), file=f)
