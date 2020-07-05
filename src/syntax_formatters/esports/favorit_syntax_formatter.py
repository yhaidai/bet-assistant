import re
from pprint import pprint, pformat
from esports.abstract_syntax_formatter import AbstractSyntaxFormatter
from syntax_formatters.favorit_syntax_formatter import FavoritSyntaxFormatter as FSF
from sample_data.csgo import favorit
import os.path


class FavoritSyntaxFormatter(AbstractSyntaxFormatter, FSF):
    def _format_win(self):
        formatted_title = self.bet_title.lower()
        if 'match winner' in formatted_title:
            formatted_title = formatted_title.replace('match winner', 'winner')
        if 'winner ' in formatted_title:
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for word in words:
                if word != 'winner':
                    formatted_title += word + ' '
            formatted_title += 'will win'
        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'odd / even' in formatted_title:
            formatted_title = formatted_title.replace('odd / even', 'total —')
        if 'total rounds' in formatted_title:
            formatted_title = formatted_title.replace('total rounds', 'total')
            formatted_title = formatted_title.replace('(', '')
            formatted_title = formatted_title.replace(')', '')
        if 'over/under games' in formatted_title:
            formatted_title = formatted_title.replace('over/under games', 'total maps')
        match = re.search(r'total maps full time (over|under)', formatted_title)
        if match:
            formatted_title = formatted_title.replace('maps ', '')
            formatted_title += ' maps'
        return formatted_title

    def _format_maps(self):
        correct_numbers = ['1-st', '2-nd', '3-rd', '4-th', '5-th']
        formatted_title = self.bet_title.lower()
        for i in range(0, len(correct_numbers)):
            if 'game ' + str(i + 1) in formatted_title:
                formatted_title = formatted_title.replace('game ' + str(i + 1) + ' ', '')
                formatted_title = correct_numbers[i] + ' map: ' + formatted_title
        return formatted_title

    def _format_handicap(self):
        formatted_title = self.bet_title.lower()
        if 'handicap rounds' or 'handicap winner' in formatted_title:
            formatted_title = formatted_title.replace('handicap rounds', 'handicap')
            formatted_title = formatted_title.replace('handicap winner', 'handicap maps')
            formatted_title = formatted_title.replace('(', '')
            formatted_title = formatted_title.replace(')', '')
        if 'handicap maps' in formatted_title:
            formatted_title = formatted_title.replace('handicap maps ', '')
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for i in range(len(words) - 1):
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
