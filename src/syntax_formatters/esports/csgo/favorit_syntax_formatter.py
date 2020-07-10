import re

from Sport import Sport
from syntax_formatters.esports.csgo.abstract_syntax_formatter import AbstractSyntaxFormatter
from syntax_formatters.esports.favorit_syntax_formatter import FavoritSyntaxFormatter as FSF
from sample_data.csgo import favorit
import os.path


class FavoritSyntaxFormatter(AbstractSyntaxFormatter, FSF):
    def _format_win_in_round(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_overtime(self):
        formatted_title = self.bet_title.lower()
        if 'full time ' in formatted_title:
            formatted_title = formatted_title.replace('full time ', '')
        return formatted_title

    def _format_total(self):
        formatted_title = self._format_total_over_under()
        if 'odd / even' in formatted_title:
            formatted_title = formatted_title.replace('odd / even', 'total —')
        if 'total rounds' in formatted_title:
            formatted_title = formatted_title.replace('total rounds', 'total')
            formatted_title = formatted_title.replace('(', '')
            formatted_title = formatted_title.replace(')', '')
        match = re.search('^total maps (over|under)', formatted_title)
        if match:
            formatted_title = formatted_title.replace('maps ', '')
            formatted_title += ' maps'
        return formatted_title

    def _format_first_to_win_number_of_rounds(self):
        formatted_title = self.bet_title.lower()
        match = re.search('which will be the first to win (\d+)', formatted_title)
        if match:
            formatted_title = formatted_title.replace('which will be the first to win ' + match.group(1) + ' rounds? ', '')
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for i in range(len(words)):
                formatted_title += words[i] + ' '
            formatted_title += 'will be first to win ' + match.group(1) + ' rounds'
        return formatted_title


if __name__ == '__main__':
    formatter = FavoritSyntaxFormatter()
    sport = Sport.from_dict(favorit.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\favorit.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
