import re
from pprint import pprint, pformat
import os.path

from sport import Sport
from football.football_abstract_syntax_formatter import FootballAbstractSyntaxFormatter
from syntax_formatters.one_x_bet_syntax_formatter import OneXBetSyntaxFormatter as OSF
from sample_data.football import one_x_bet


class FootballOneXBetSyntaxFormatter(FootballAbstractSyntaxFormatter, OSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the 1xbet website
    """
    def _format_win(self):
        formatted_title = self.bet_title.lower()
        if '1x2.' in formatted_title:
            formatted_title = formatted_title.replace('1x2.', 'will win')
            formatted_title = formatted_title.replace('will win draw', 'draw will win')
            self._move_teams_left(formatted_title)

        return formatted_title

    def _format_handicap(self):
        formatted_title = self.bet_title.lower()
        # if 'handicap' in formatted_title:
            # print(formatted_title)
        found = re.search(r'handicap (\+|-)\d+(\.\d+)?$', formatted_title)
        if found:
            formatted_title += ' goals'
        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        for c in ['handicap. ', 'total 1. ', 'total 2. ', 'individual ', 'total. ', 'even/odd. ']:
            if c in formatted_title:
                formatted_title = formatted_title.replace(c, '')
        formatted_title = formatted_title.replace('team ', '')
        match = re.search(r'((asian|total) (1|2) )', formatted_title)
        if match:
            teams = self.match_title.raw_teams
            formatted_title = formatted_title.replace(match.group(1), teams[int(match.group(3)) - 1]
                                                      + ' ' + match.group(2) + ' ')
        match = re.search(r'total (over|under)', formatted_title)
        if match:
            formatted_title = formatted_title.replace('total', 'total goals')
        return formatted_title

    def _format_halves(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'((1|2) half\. )', formatted_title)
        if match:
            formatted_title = formatted_title.replace('1 half.', '1-st half')
            formatted_title = formatted_title.replace('2 half.', '2-nd half')
        match = re.search(r'( (1-st|2-nd) half)', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), '')
            formatted_title = match.group(2) + ' half ' + formatted_title
        return formatted_title

    def _format_double_chance(self):
        formatted_title = self.bet_title.lower()
        if 'double chance' in formatted_title:
            teams = self.match_title.raw_teams
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

    def _format_uncommon_chars(self):
        formatted_title = self.bet_title.lower()

        # these are different characters :)
        formatted_title = formatted_title.replace('с', 'c')
        formatted_title = formatted_title.replace('–', '-')

        return formatted_title


if __name__ == '__main__':
    formatter = FootballOneXBetSyntaxFormatter()
    sport = Sport.from_dict(one_x_bet.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\one_x_bet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
