import re
from pprint import pprint, pformat

from Sport import Sport
from csgo.abstract_syntax_formatter import AbstractSyntaxFormatter
from esports.marathon_syntax_formatter import MarathonSyntaxFormatter as MSF
from esports.abstract_syntax_formatter import AbstractSyntaxFormatter as EASF
from sample_data.csgo import marathon
import os.path


class MarathonSyntaxFormatter(AbstractSyntaxFormatter, MSF):
    def _format_win_in_round(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_overtime(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_teams(self):
        return self._move_teams_left()


if __name__ == '__main__':
    formatter = MarathonSyntaxFormatter()
    sport = Sport.from_dict(marathon.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\marathon.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
