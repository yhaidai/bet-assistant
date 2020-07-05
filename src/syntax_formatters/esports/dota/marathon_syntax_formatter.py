from pprint import pprint, pformat
from dota.abstract_syntax_formatter import AbstractSyntaxFormatter
from esports.marathon_syntax_formatter import MarathonSyntaxFormatter as MSF
from sample_data.dota import marathon
import os.path


class MarathonSyntaxFormatter(AbstractSyntaxFormatter, MSF):
    def _format_win_in_round(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_overtime(self):
        formatted_title = self.bet_title.lower()
        return formatted_title


if __name__ == '__main__':
    formatter = MarathonSyntaxFormatter()
    formatter.apply_unified_syntax_formatting(marathon.bets)
    pprint(formatter.bets)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\marathon.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('bets =', pformat(formatter.bets), file=f)