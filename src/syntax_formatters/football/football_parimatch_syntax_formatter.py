import re
from pprint import pprint, pformat
import os.path

from sport import Sport
from football.football_abstract_syntax_formatter import FootballAbstractSyntaxFormatter
from syntax_formatters.parimatch_syntax_formatter import ParimatchSyntaxFormatter as PSF
from sample_data.football import parimatch
from syntax_formatters.match_title_compiler import MatchTitleCompiler


class FootballParimatchSyntaxFormatter(FootballAbstractSyntaxFormatter, PSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the parimatch website
    """
    def _format_handicap(self):
        formatted_title = self.bet_title.lower()

        if 'handicap' in formatted_title:
            formatted_title = self._swap_substrings(formatted_title, '. ', 1, 2, '')
            formatted_title = formatted_title.replace('handicap value', '', 1).replace('coefficient', '', 1)

        found = re.search(r'handicap (\+|-|–)\d+\.\d+$', formatted_title)
        if found:
            formatted_title += ' goals'

        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        formatted_title = formatted_title.replace('totals', 'total')
        if 'total' in formatted_title:
            formatted_title = self._swap_substrings(formatted_title, '. ', 1, 2, ' ')
        match = re.search(r'total (over|under)', formatted_title)
        if match:
            formatted_title = formatted_title.replace('total', 'total goals')

        return formatted_title

    @staticmethod
    def _swap_substrings(text, pattern, id1, id2, separator):
        substrings = text.split(pattern)
        temp = substrings[id1]
        substrings[id1] = substrings[id2]
        substrings[id2] = temp

        result = ''
        for s in substrings:
            result += s + separator

        tail_length = len(separator)
        if tail_length > 0:
            result = result[:-tail_length]

        return result

    def _format_win(self):
        formatted_title = self.bet_title.lower()
        team_names = self.match_title.raw_teams

        if 'win of' in formatted_title:
            if formatted_title.find('1st') != -1:
                team_number = '1st'
                team_name = team_names[0]
            elif formatted_title.find('2nd') != -1:
                team_number = '2nd'
                team_name = team_names[1]
            else:
                raise NotImplementedError('Not "1st" nor "2nd" was found')
            to_be_replaced = 'win of the ' + team_number
            formatted_title = formatted_title.replace(to_be_replaced, team_name + ' will win', 1)
        elif 'home win' in formatted_title:
            formatted_title = formatted_title.replace('home', team_names[0] + ' will')
        elif 'away win' in formatted_title:
            formatted_title = formatted_title.replace('away', team_names[1] + ' will')
        elif 'draw' in formatted_title:
            formatted_title += ' will win'
        if 'win or draw' in formatted_title:
            formatted_title = formatted_title.replace('win or draw', 'lose')

        return formatted_title

    def _format_uncommon_chars(self):
        formatted_title = self.bet_title.lower()
        formatted_title = formatted_title.replace('–', '-')
        formatted_title = formatted_title.replace(':', '')

        return formatted_title

    def _format_teams(self):
        return self._move_teams_left()


if __name__ == '__main__':
    formatter = FootballParimatchSyntaxFormatter()
    sport = Sport.from_dict(parimatch.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\parimatch.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
