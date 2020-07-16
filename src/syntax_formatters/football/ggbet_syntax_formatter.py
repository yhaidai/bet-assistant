import re
from pprint import pprint, pformat

from sport import Sport
from football.abstract_syntax_formatter import AbstractSyntaxFormatter
from syntax_formatters.ggbet_syntax_formatter import GGBetSyntaxFormatter as GSF
from sample_data.football import ggbet
import os.path


class GGBetSyntaxFormatter(AbstractSyntaxFormatter, GSF):
    def _format_win(self):
        formatted_title = self.bet_title.lower()
        if '1x2' in formatted_title:
            formatted_title = formatted_title.replace('1x2', 'will win')
            formatted_title = formatted_title.replace('will win draw', 'draw will win')
        return formatted_title

    def _format_handicap(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'handicap (\+|-)\d+\.\d+$', formatted_title)
        if found:
            formatted_title += ' goals'
        return formatted_title

    def _format_halves(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'(1st|2nd) half', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), match.group(1)[0] + '-' + match.group(1)[1:])
        match = re.search(r'^(1-st|2-nd) half', formatted_title)
        if match:
            return formatted_title
        match = re.search(r'( (1-st|2-nd) half)', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), '')
            formatted_title = match.group(2) + ' half ' + formatted_title
        return formatted_title

    def _format_double_chance(self):
        formatted_title = self.bet_title.lower()
        if 'double chance' in formatted_title:
            teams = self.get_teams()
            if teams[0] in formatted_title:
                if teams[1] in formatted_title:
                    formatted_title = 'draw will lose'
                else:
                    formatted_title = teams[1] + ' will lose'
            else:
                formatted_title = teams[0] + ' will lose'
        return formatted_title

    def _remove_full_time(self):
        formatted_title = self.bet_title.lower()
        if 'full time' in formatted_title:
            formatted_title = formatted_title.replace('full time ', '')
        for c in ['(', ')', '- ']:
            formatted_title = formatted_title.replace(c, '')
        return formatted_title

    def _format_before(self, bets):
        bets = self._update(bets, self._remove_full_time)
        bets = self._update(bets, self._format_whitespaces)
        return bets

    def _format_whitespaces(self):
        formatted_title = self.bet_title.lower()
        formatted_title = ' '.join(formatted_title.split())
        formatted_title = formatted_title.strip()
        return formatted_title

    def _format_after(self, bets):
        return bets

    def _format_teams(self):
        return self._move_teams_left()


if __name__ == '__main__':
    formatter = GGBetSyntaxFormatter()
    sport = Sport.from_dict(ggbet.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\ggbet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
