import re
from syntax_formatters.esports.esports_abstract_syntax_formatter import EsportsAbstractSyntaxFormatter
from syntax_formatters.favorit_syntax_formatter import FavoritSyntaxFormatter as FSF


class EsportsFavoritSyntaxFormatter(EsportsAbstractSyntaxFormatter, FSF):
    def _format_win(self):
        formatted_title = self.bet_title.lower()
        if 'match winner' in formatted_title:
            formatted_title = formatted_title.replace('match winner', 'winner')
        if 'winner' in formatted_title:
            formatted_title = formatted_title.replace('winner', 'will win')
        if '1 x 2' in formatted_title:
            formatted_title = formatted_title.replace('1 x 2', 'will win')
            formatted_title = formatted_title.replace('will win draw', 'draw will win')
        found = re.search(r'draw (yes|no)', formatted_title)
        if found:
            if found.group(1) == 'yes':
                formatted_title = formatted_title.replace('draw yes', 'draw will win')
            else:
                formatted_title = formatted_title.replace('draw no', 'draw will lose')

        return formatted_title

    def _format_total(self):
        formatted_title = self._format_total_over_under()
        return formatted_title

    def _format_total_over_under(self):
        formatted_title = self.bet_title.lower()
        if 'over/under games' in formatted_title:
            formatted_title = formatted_title.replace('over/under games', 'total maps')
        return formatted_title

    def _format_frags(self):
        formatted_title = self.bet_title.lower()
        if 'frag' in formatted_title:
            formatted_title = formatted_title.replace('frag', 'kill')
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
        match = re.search(r'(kills ((\+|-)(\d+\.\d)))', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), match.group(2) + ' kills')
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

    def _remove_full_time(self):
        formatted_title = self.bet_title.lower()
        if 'full time' in formatted_title:
            formatted_title = formatted_title.replace('full time ', '')
        return formatted_title

    def _format_before(self, bets):
        bets = self._update(bets, self._remove_full_time)
        bets = self._update(bets, self._format_frags)
        return bets
