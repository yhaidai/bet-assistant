import re
from esports.abstract_syntax_formatter import AbstractSyntaxFormatter
from syntax_formatters.ggbet_syntax_formatter import GGBetSyntaxFormatter as GSF


class GGBetSyntaxFormatter(AbstractSyntaxFormatter, GSF):
    def _format_win(self):
        formatted_title = self.bet_title.lower()
        if 'winner ' in formatted_title:
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for word in words:
                if word != 'winner':
                    formatted_title += word + ' '
            formatted_title += 'will win'
        if '1x2' in formatted_title:
            formatted_title = formatted_title.replace('1x2 ', '')
            formatted_title += ' will win'
        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'odd/even maps' in formatted_title:
            formatted_title = formatted_title.replace('odd/even maps', 'total maps')
        if 'odd/even' in formatted_title:
            formatted_title = formatted_title.replace('odd/even ', '')
        return formatted_title

    def _format_maps(self):
        correct_numbers = ['1-st', '2-nd', '3-rd', '4-th', '5-th']
        invalid_numbers = ['1st', '2nd', '3rd', '4th', '5th']
        formatted_title = self.bet_title.lower()
        for i in range(len(correct_numbers)):
            if invalid_numbers[i] + ' map' in formatted_title:
                formatted_title = formatted_title.replace(invalid_numbers[i] + ' map', correct_numbers[i] + ' map:')
        for i in range(len(correct_numbers)):
            if 'map ' + str(i + 1) in formatted_title:
                formatted_title = formatted_title.replace('map ' + str(i + 1), correct_numbers[i] + ' map:')
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

    def _format_whitespaces(self):
        formatted_title = self.bet_title.lower()
        formatted_title = ' '.join(formatted_title.split())
        formatted_title = formatted_title.strip()
        return formatted_title

    def __format_before(self):
        formatted_title = self.bet_title.lower()
        if ' - ' in formatted_title:
            formatted_title = formatted_title.replace(' - ', ' ')
        if 'terrorist' in formatted_title:
            formatted_title = formatted_title.replace('terrorist', 't')
        return formatted_title

    def _format_before(self, bets):
        bets = self._update(bets, self._format_whitespaces)
        bets = self._update(bets, self.__format_before)
        return bets

    def _format_after(self, bets):
        return bets
