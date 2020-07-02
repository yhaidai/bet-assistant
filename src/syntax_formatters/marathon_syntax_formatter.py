import re
from pprint import pprint
from abstract_syntax_formatter import AbstractSyntaxFormatter
from scrapers.sample_data import marathon


class MarathonSyntaxFormatter(AbstractSyntaxFormatter):
    _NAME = 'marathon'

    def _format_before(self, bets):
        bets = self._update(bets, self._format_whitespaces)
        bets = self._update(bets, self.__format_before)
        return bets

    def _format_after(self, bets):
        bets = self._update(bets, self.__format_after)
        return bets

    def _get_name(self):
        return self._NAME

    def _format_whitespaces(self):
        formatted_title = self.bet_title.lower()
        formatted_title = ' '.join(formatted_title.split())
        formatted_title = formatted_title.strip()
        return formatted_title

    def __format_before(self):
        formatted_title = self.bet_title.lower()
        for char in ['(', ')', 'result ']:
            formatted_title = formatted_title.replace(char, '')
        return formatted_title

    def __format_after(self):
        formatted_title = self.bet_title.lower()
        formatted_title = formatted_title.replace('- ', '')
        return formatted_title

    def _format_win(self):
        formatted_title = self.bet_title.lower()
        formatted_title = formatted_title.replace('to win', 'will win')
        return formatted_title

    def _format_win_in_round(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'total rounds' in formatted_title:
            formatted_title = formatted_title.replace('total rounds ', 'total ')
        if 'total maps' in formatted_title:
            formatted_title = formatted_title.replace('total maps ', 'total ')
        return formatted_title

    def _format_maps(self):
        CORRECT_NUMBERS = ['1-st', '2-nd', '3-rd', '4-th', '5-th']
        INVALID_NUMBERS = ['1st', '2nd', '3rd', '4th', '5th']
        formatted_title = self.bet_title.lower()
        for i in range(0, len(CORRECT_NUMBERS)):
            if INVALID_NUMBERS[i] + ' map' in formatted_title:
                formatted_title = formatted_title.replace(INVALID_NUMBERS[i] + ' map ', '')
                words = re.split(' ', formatted_title)
                formatted_title = CORRECT_NUMBERS[i] + ' map: '
                for i in range(len(words)):
                    formatted_title += words[i] + ' '
                formatted_title = formatted_title[:-1]
        return formatted_title

    def _format_handicap(self):
        formatted_title = self.bet_title.lower()
        if 'to win match with handicap by maps' in formatted_title:
            formatted_title = formatted_title.replace('to win match with handicap by maps', 'handicap maps')
        if 'to win match with handicap by rounds' in formatted_title:
            formatted_title = formatted_title.replace('to win match with handicap by rounds', 'handicap')
        if 'to win with handicap by rounds' in formatted_title:
            formatted_title = formatted_title.replace('to win with handicap by rounds', 'handicap')
        if 'handicap maps' in formatted_title:
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for i in range(2, len(words)-1):
                formatted_title += words[i] + ' '
            formatted_title += 'handicap ' + words[-1] + ' maps'
        return formatted_title

    def _format_uncommon_chars(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_correct_score(self):
        formatted_title = self.bet_title.lower()
        if 'correct score' in formatted_title:
            formatted_title = formatted_title.replace(' - ', '-')
            words = re.split(' ', formatted_title)
            formatted_title = 'correct score ' + words[-1]
        return formatted_title

    def _format_first_frag(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_overtime(self):
        formatted_title = self.bet_title.lower()
        return formatted_title


if __name__ == '__main__':
    formatter = MarathonSyntaxFormatter()
    formatter.apply_unified_syntax_formatting(marathon.bets)
    pprint(formatter.bets)