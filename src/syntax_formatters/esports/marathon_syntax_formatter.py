import re
from esports.abstract_syntax_formatter import AbstractSyntaxFormatter
from syntax_formatters.marathon_syntax_formatter import MarathonSyntaxFormatter as MSF


class MarathonSyntaxFormatter(AbstractSyntaxFormatter, MSF):
    def _format_before(self, bets):
        bets = self._update(bets, self._format_whitespaces)
        bets = self._update(bets, self.__format_before)
        return bets

    def _format_after(self, bets):
        bets = self._update(bets, self.__format_after)
        return bets

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

    def _format_maps(self):
        correct_numbers = ['1-st', '2-nd', '3-rd', '4-th', '5-th']
        invalid_numbers = ['1st', '2nd', '3rd', '4th', '5th']
        formatted_title = self.bet_title.lower()
        for i in range(0, len(correct_numbers)):
            if invalid_numbers[i] + ' map' in formatted_title:
                formatted_title = formatted_title.replace(invalid_numbers[i] + ' map ', '')
                words = re.split(' ', formatted_title)
                formatted_title = correct_numbers[i] + ' map: '
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

    def _format_correct_score(self):
        formatted_title = self.bet_title.lower()
        if 'correct score' in formatted_title:
            formatted_title = formatted_title.replace(' - ', '-')
            words = re.split(' ', formatted_title)
            formatted_title = 'correct score ' + words[-1]
        return formatted_title
