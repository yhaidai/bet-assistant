import re
from pprint import pprint, pformat
from dota.abstract_syntax_formatter import AbstractSyntaxFormatter
from esports.ggbet_syntax_formatter import GGBetSyntaxFormatter as GSF
from sample_data.dota import ggbet
import os.path


class GGBetSyntaxFormatter(AbstractSyntaxFormatter, GSF):
    def _format_win_in_round(self):
        formatted_title = self.bet_title.lower()
        if '2nd pistol round winner' in formatted_title:
            formatted_title = formatted_title.replace('2nd pistol round winner', 'will win round in 16')
            index = formatted_title.find('will win in round 16')
            head = formatted_title[:index - 1]
            tail = formatted_title[index + len('will win in round 16'):]
            formatted_title = head + tail + ' will win in round 16'
        if '1st pistol round winner ' in formatted_title:
            formatted_title = formatted_title.replace('1st pistol round winner ', 'will win in round 1')
            index = formatted_title.find('will win in round 1')
            head = formatted_title[:index - 1]
            tail = formatted_title[index + len('will win in round 1'):]
            formatted_title = head + ' ' + tail + ' will win in round 1'
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
        if 'race to  rounds' in formatted_title:
            formatted_title = formatted_title.replace('race to  rounds ', '')
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for i in range(0, len(words) - 1):
                formatted_title += words[i] + ' '
            formatted_title += 'will be first to win ' + words[-1] + ' rounds'
        return formatted_title


if __name__ == '__main__':
    formatter = GGBetSyntaxFormatter()
    formatter.apply_unified_syntax_formatting(ggbet.bets)
    pprint(formatter.bets)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\ggbet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('bets =', pformat(formatter.bets), file=f)