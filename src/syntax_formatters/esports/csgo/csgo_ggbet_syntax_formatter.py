import re

from sport import Sport
from syntax_formatters.esports.csgo.csgo_abstract_syntax_formatter import CSGOAbstractSyntaxFormatter
from syntax_formatters.esports.esports_ggbet_syntax_formatter import EsportsGGBetSyntaxFormatter as GSF
from sample_data.csgo import ggbet
import os.path


class CSGOGGBetSyntaxFormatter(CSGOAbstractSyntaxFormatter, GSF):
    def _format_win_in_round(self):
        formatted_title = self.bet_title.lower()
        found = re.search('(1st pistol round winner (1|2))', formatted_title)
        if found:
            formatted_title = formatted_title.replace(' ' + found.group(1), '')
            if found.group(2) == '1':
                formatted_title += ' will win in round 1'
            else:
                formatted_title += ' will win in round 16'
        return formatted_title

    def _format_overtime(self):
        formatted_title = self.bet_title.lower()
        overtime_substrings = ('(incl. overtime) ', '(incl. overtimes) ', 'incl. overtime ', 'incl. overtimes ')
        for overtime_substring in overtime_substrings:
            if overtime_substring in formatted_title:
                formatted_title = formatted_title.replace(overtime_substring, '')
        if 'will there be overtime' in formatted_title:
            formatted_title = formatted_title.replace('will there be overtime', 'overtime')
        return formatted_title

    def _format_first_to_win_number_of_rounds(self):
        formatted_title = self.bet_title.lower()
        if 'race to rounds' in formatted_title:
            formatted_title = formatted_title.replace('race to rounds ', '')
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for i in range(0, len(words) - 1):
                formatted_title += words[i] + ' '
            formatted_title += 'will be first to win ' + words[-1] + ' rounds'
        return formatted_title

    def _format_handicap(self):
        formatted_title = GSF._format_handicap(self)
        if 'handicap' in formatted_title and ' maps' not in formatted_title:
            formatted_title += ' rounds'

        return formatted_title


if __name__ == '__main__':
    formatter = CSGOGGBetSyntaxFormatter()
    sport = Sport.from_dict(ggbet.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\ggbet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
