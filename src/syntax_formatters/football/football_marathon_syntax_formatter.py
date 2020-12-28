import re

from sport import Sport
from syntax_formatters.football.football_abstract_syntax_formatter import FootballAbstractSyntaxFormatter
from syntax_formatters.marathon_syntax_formatter import MarathonSyntaxFormatter as MSF
from sample_data.football import marathon
import os.path


class FootballMarathonSyntaxFormatter(FootballAbstractSyntaxFormatter, MSF):
    def _format_win(self):
        formatted_title = self.bet_title.lower()
        formatted_title = formatted_title.replace('to win', 'will win')
        formatted_title = formatted_title.replace('draw', 'draw will win')
        return formatted_title

    def _format_handicap(self):
        formatted_title = self.bet_title.lower()
        formatted_title = formatted_title.replace('to win match with ', '')
        found = re.search(r'handicap (\+|-)?\d+\.\d+$', formatted_title)
        if found:
            if not found.group(1):
                formatted_title = formatted_title.replace('handicap ', 'handicap +')
            formatted_title += ' goals'
        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'(((\+|-)?\d(\.\d)?),((\+|-)?\d\.\d))', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1),
                                                      str((float(match.group(2)) + float(match.group(5)))/2))
        match = re.search(r'((\d\.\d+) (over|under))', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), '')
            formatted_title += match.group(3) + ' ' + match.group(2)

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

    def _format_time(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'(from 1 to \d\d min. )', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), '')
            formatted_title = match.group(1) + formatted_title
        return formatted_title

    def _format_double_chance(self):
        formatted_title = self.bet_title.lower()
        teams = self.match_title.get_teams()
        match = re.search('will win( or .+? will win)', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), '')
            if 'draw' in match.group(1):
                formatted_title = self.swap_teams(formatted_title)
            else:
                for team in teams:
                    formatted_title = formatted_title.replace(team, 'draw')
            formatted_title = formatted_title.replace('will win', 'will lose')
        return formatted_title

    def _remove_full_time(self):
        formatted_title = self.bet_title.lower()
        if 'full time' in formatted_title:
            formatted_title = formatted_title.replace('full time ', '')
        for c in ['(', ')', '- ', '\n', 'result ', 'result, ']:
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

    def _format_correct_score(self):
        formatted_title = self.bet_title.lower()
        found = re.search('^((\d-(st|nd) half )?correct score \d+ \d+)', formatted_title)
        if found:
            formatted_title = found.group(1)
        return formatted_title


if __name__ == '__main__':
    formatter = FootballMarathonSyntaxFormatter()
    sport = Sport.from_dict(marathon.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\marathon.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)