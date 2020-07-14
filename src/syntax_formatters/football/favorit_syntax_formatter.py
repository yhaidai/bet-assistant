import re
from pprint import pprint, pformat

from Sport import Sport
from football.abstract_syntax_formatter import AbstractSyntaxFormatter
from syntax_formatters.favorit_syntax_formatter import FavoritSyntaxFormatter as FSF
from sample_data.football import favorit
import os.path


class FavoritSyntaxFormatter(AbstractSyntaxFormatter, FSF):
    def _format_win(self):
        formatted_title = self.bet_title.lower()
        if 'match winner' in formatted_title:
            formatted_title = formatted_title.replace('match winner', 'winner')
        if 'winner' in formatted_title:
            formatted_title = formatted_title.replace('winner', 'will win')
        if '1 x 2' in formatted_title:
            formatted_title = formatted_title.replace('1 x 2', 'will win')
            formatted_title = formatted_title.replace('will win draw', 'draw will win')
        return formatted_title

    def _remove_full_time(self):
        formatted_title = self.bet_title.lower()
        if 'full time' in formatted_title:
            formatted_title = formatted_title.replace('full time ', '')
        for c in ['(', ')', '- ']:
            formatted_title = formatted_title.replace(c, '')
        if '&nbsp;' in formatted_title:
            formatted_title = formatted_title.replace('&nbsp;', ' ')
        return formatted_title

    def _format_double_chance(self):
        formatted_title = self.bet_title.lower()
        if 'double chance' in formatted_title:
            teams = self.get_teams()
            if '12' in formatted_title:
                formatted_title = 'draw will lose'
            elif '1x' in formatted_title:
                formatted_title = teams[1] + ' will lose'
            else:
                formatted_title = teams[0] + ' will lose'
        return formatted_title

    def _format_halves(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'(1st|2nd)', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), match.group(1)[0] + '-' + match.group(1)[1:])
        match = re.search(r'^(1-st|2-nd)', formatted_title)
        if match:
            return formatted_title
        match = re.search(r'( (1-st|2-nd) half)', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), '')
            formatted_title = match.group(2) + ' half ' + formatted_title
        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        for c in ['over/under', 'odd / even']:
            if c in formatted_title:
                formatted_title = formatted_title.replace(c, 'total goals')
        if 'asian total' in formatted_title:
            formatted_title = formatted_title.replace('asian total', 'asian total goals')
        return formatted_title

    def _format_before(self, bets):
        bets = self._update(bets, self._remove_full_time)

        return bets

    def _format_teams(self):
        return self._move_teams_left()





if __name__ == '__main__':
    formatter = FavoritSyntaxFormatter()
    sport = Sport.from_dict(favorit.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\favorit.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
