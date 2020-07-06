import re
from pprint import pprint, pformat

from Sport import Sport
from csgo.abstract_syntax_formatter import AbstractSyntaxFormatter
from esports.marathon_syntax_formatter import MarathonSyntaxFormatter as MSF
from sample_data.csgo import marathon
import os.path


class MarathonSyntaxFormatter(AbstractSyntaxFormatter, MSF):
    def _format_win_in_round(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_overtime(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'total rounds' in formatted_title:
            formatted_title = formatted_title.replace('total rounds ', 'total ')
        match = re.search('total maps (over|under)', formatted_title)
        if match:
            formatted_title = formatted_title.replace('maps ', '')
            formatted_title += ' maps'
        match = re.search('(even|odd)', formatted_title)
        if match:
            formatted_title = formatted_title.replace(' ' + match.group(1), ' — ' + match.group(1))

        return formatted_title


if __name__ == '__main__':
    formatter = MarathonSyntaxFormatter()
    sport = Sport.from_dict(marathon.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\marathon.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
