import re
from syntax_formatters.esports.abstract_syntax_formatter import AbstractSyntaxFormatter
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
        if '-total' in formatted_title:
            formatted_title = formatted_title.replace('-total', 'total')
        return formatted_title

    def _format_win(self):
        formatted_title = self.bet_title.lower()
        formatted_title = formatted_title.replace('to win', 'will win')
        formatted_title = formatted_title.replace('draw', 'draw will win')
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
        match = re.search(r'(handicap maps ((\+|-)\d\.\d))', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), 'handicap ' + match.group(2) + ' maps')
        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        match = re.search('total maps .+? (over|under)', formatted_title)
        if match:
            formatted_title = formatted_title.replace(' ' + match.group(1), '')
            formatted_title = formatted_title.replace('total maps ', 'total maps ' + match.group(1) + ' ')
        match = re.search('((\d\d\.\d) (over|under))', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), '')
            formatted_title += match.group(3) + ' ' + match.group(2)

        return formatted_title

    def _format_correct_score(self):
        formatted_title = self.bet_title.lower()
        if 'correct score' in formatted_title:
            formatted_title = formatted_title.replace(' - ', '-')
            words = re.split(' ', formatted_title)
            formatted_title = 'correct score ' + words[-1]
        return formatted_title
