import re
from pprint import pprint, pformat
from abstract_syntax_formatter import AbstractSyntaxFormatter
from scrapers.sample_data import ggbet
import os.path

class GGBetSyntaxFormatter(AbstractSyntaxFormatter):
    _NAME = 'ggbet'

    def _format_after(self, bets):
        bets = self._update(bets, self._format_overtime)
        return bets

    def _format_before(self, bets):
        return bets

    def _get_name(self):
        return self._NAME

    def _format_win(self):
        formatted_title = self.bet_title.lower()
        if 'winner ' in formatted_title:
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for word in words:
                if word != 'winner':
                    formatted_title += word + ' '
            formatted_title += 'will win'
        return formatted_title

    def _format_win_in_round(self):
        formatted_title = self.bet_title.lower()
        if '2nd pistol round winner' in formatted_title:
            formatted_title = formatted_title.replace('2nd pistol round winner', 'will win round 16')
            index = formatted_title.find('will win round 16')
            head = formatted_title[:index - 1]
            tail = formatted_title[index + len('will win round 16'):]
            formatted_title = head + tail + ' will win round 16'
        if '1st pistol round winner ' in formatted_title:
            formatted_title = formatted_title.replace('1st pistol round winner ', 'will win round 1')
            index = formatted_title.find('will win round 1')
            head = formatted_title[:index - 1]
            tail = formatted_title[index + len('will win round 1'):]
            formatted_title = head + ' ' + tail + ' will win round 1'
        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'total rounds' in formatted_title:
            formatted_title = formatted_title.replace('total rounds', 'total')
        return formatted_title

    def _format_maps(self):
        correct_numbers = ['1-st', '2-nd', '3-rd', '4-th', '5-th']
        invalid_numbers = ['1st', '2nd', '3rd', '4th', '5th']
        formatted_title = self.bet_title.lower()
        for i in range(0, len(correct_numbers)):
            if invalid_numbers[i] + ' map -' in formatted_title:
                formatted_title = formatted_title.replace(invalid_numbers[i] + ' map -', correct_numbers[i] + ' map:')
            if 'map ' + str(i + 1) + ' -' in formatted_title:
                formatted_title = formatted_title.replace('map ' + str(i + 1) + ' -', correct_numbers[i] + ' map:')
        return formatted_title

    def _format_handicap(self):
        formatted_title = self.bet_title.lower()
        if 'round handicap' or 'rounds handicap' in formatted_title:
            formatted_title = formatted_title.replace('round handicap', 'handicap')
            formatted_title = formatted_title.replace('rounds handicap', 'handicap')
            formatted_title = formatted_title.replace('(', '')
            formatted_title = formatted_title.replace(')', '')
        if 'map handicap' in formatted_title:
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for i in range(2, len(words) - 1):
                formatted_title += words[i] + ' '
            formatted_title += 'handicap ' + words[-1] + ' maps'
        return formatted_title

    def _format_uncommon_chars(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_correct_score(self):
        formatted_title = self.bet_title.lower()
        if 'correct map score' in formatted_title:
            formatted_title = formatted_title.replace('correct map score', 'correct score')
        if 'correct score' in formatted_title:
            formatted_title = formatted_title[::-1]
            formatted_title = formatted_title.replace(':', '-', 1)
            formatted_title = formatted_title[::-1]
        return formatted_title

    def _format_overtime(self):
        formatted_title = self.bet_title.lower()
        overtime_substrings = ('(incl. overtime) ', '(incl. overtimes) ', 'incl. overtime ', 'incl. overtimes ')
        for overtime_substring in overtime_substrings:
            if overtime_substring in formatted_title:
                formatted_title = formatted_title.replace(overtime_substring, '')
        return formatted_title


if __name__ == '__main__':
    formatter = GGBetSyntaxFormatter()
    formatter.apply_unified_syntax_formatting(ggbet.bets)
    pprint(formatter.bets)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\ggbet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('bets = ', pformat(formatter.bets), file=f)