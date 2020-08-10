import re

from sport import Sport
from football.football_abstract_syntax_formatter import FootballAbstractSyntaxFormatter
from syntax_formatters.favorit_syntax_formatter import FavoritSyntaxFormatter as FSF
from sample_data.football import favorit
import os.path


class FootballFavoritSyntaxFormatter(FootballAbstractSyntaxFormatter, FSF):
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

    def _format_handicap(self):
        formatted_title = self.bet_title.lower()
        for c in ['yellow cards ', 'corners ']:
            if c + 'handicap' in formatted_title:
                formatted_title = formatted_title.replace(c, '')
                formatted_title += ' ' + c
        found = re.search(r'handicap (\+|-)\d+\.\d+$', formatted_title)
        if found:
            formatted_title += ' goals'
        return formatted_title

    def _remove_full_time(self):
        formatted_title = self.bet_title.lower()
        # if '' in formatted_title:
        #     formatted_title = formatted_title.replace('full time ', '')
        for c in ['(', ')', '- ', 'full time ']:
            formatted_title = formatted_title.replace(c, '')
        if '&nbsp;' in formatted_title:
            formatted_title = formatted_title.replace('&nbsp;', ' ')
        return formatted_title

    def _format_double_chance(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'(double chance (12|1x|x2))', formatted_title)
        if found:
            teams = self.match_title.raw_teams
            if found.group(2) == '12':
                formatted_title = formatted_title.replace(found.group(1), 'draw will lose')
            if found.group(2) == '1x':
                formatted_title = formatted_title.replace(found.group(1), teams[1] + ' will lose')
            if found.group(2) == 'x2':
                formatted_title = formatted_title.replace(found.group(1), teams[0] + ' will lose')
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
                formatted_title = formatted_title.replace(c, 'total')
        found = re.search(r'odd/even (even|odd)', formatted_title)
        if found:
            formatted_title = formatted_title.replace('odd/even ', '')
        found = re.search(r'total ((over|under)|(even|odd))', formatted_title)
        if found:
            formatted_title = formatted_title.replace('total', 'total goals')
        return formatted_title

    def _format_before(self, bets):
        bets = self._update(bets, self._remove_full_time)

        return bets

    def _format_teams(self):
        return self._move_teams_left()


if __name__ == '__main__':
    formatter = FootballFavoritSyntaxFormatter()
    sport = Sport.from_dict(favorit.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\favorit.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
