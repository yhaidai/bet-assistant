import re

from sport import Sport
from syntax_formatters.esports.lol.lol_abstract_syntax_formatter import LoLAbstractSyntaxFormatter
from syntax_formatters.esports.esports_favorit_syntax_formatter import EsportsFavoritSyntaxFormatter as FSF
from sample_data.lol import favorit
import os.path


class LoLFavoritSyntaxFormatter(LoLAbstractSyntaxFormatter, FSF):
    def _format_individual_total_kills(self):
        formatted_title = self.bet_title.lower()
        if 'team total' in formatted_title:
            formatted_title = formatted_title.replace('team total ', '')
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for i in range(len(words) - 2):
                formatted_title += words[i] + ' '
            formatted_title += 'total kills ' + words[-2] + ' ' + words[-1]
        return formatted_title

    def _format_first_to_make_number_of_kills(self):
        formatted_title = self.bet_title.lower()
        if 'race to kills' in formatted_title:
            formatted_title = formatted_title.replace('race to kills ', '')
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for i in range(len(words) - 1):
                formatted_title += words[i] + ' '
            formatted_title += 'will first make ' + words[-1] + ' kills'
        return formatted_title

    def _format_first_to_kill(self):
        formatted_title = self.bet_title.lower()
        if 'kill first baron' in formatted_title:
            formatted_title = formatted_title.replace('kill first baron', 'will first kill baron')
        return formatted_title

    def _format_total(self):
        formatted_title = self._format_total_over_under()
        if 'odd / even' in formatted_title:
            formatted_title = formatted_title.replace('odd / even', 'total kills')
        return formatted_title

    def _format_most_kills(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_draw(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_first_kill(self):
        formatted_title = self.bet_title.lower()
        # print(formatted_title)
        if 'which team will be the first to make a kill?' in formatted_title:
            formatted_title = formatted_title.replace('which team will be the first to make a kill?', 'first blood')
        return formatted_title

    def _format_map_duration(self):
        formatted_title = self.bet_title.lower()
        if 'map duration' in formatted_title:
            formatted_title = formatted_title.replace('map duration', 'duration')
            formatted_title = formatted_title.replace(' minutes', '')
        return formatted_title

    def _format_first_to_destroy(self):
        formatted_title = self.bet_title.lower()
        if 'which team will be the first to lose a turret?' in formatted_title:
            formatted_title = formatted_title.replace('which team will be the first to lose a turret?',
                                                      'will first destroy turret')
            formatted_title = self.swap_teams(formatted_title)
        return formatted_title

    def _format_teams(self):
        return self._move_teams_left()


if __name__ == '__main__':
    formatter = LoLFavoritSyntaxFormatter()
    sport = Sport.from_dict(favorit.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\favorit.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
