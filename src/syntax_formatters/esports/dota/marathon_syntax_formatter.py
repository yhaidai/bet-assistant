import re

from Sport import Sport
from syntax_formatters.esports.dota.abstract_syntax_formatter import AbstractSyntaxFormatter
from syntax_formatters.esports.marathon_syntax_formatter import MarathonSyntaxFormatter as MSF
from sample_data.dota import marathon
import os.path


class MarathonSyntaxFormatter(AbstractSyntaxFormatter, MSF):

    def _format_individual_total_kills(self):
        formatted_title = self.bet_title.lower()
        match = re.search('total kills .+? (even|odd)', formatted_title)
        if match:
            formatted_title = formatted_title.replace('total kills ', '')
            formatted_title = formatted_title.replace(' ' + match.group(1), '')
            formatted_title += ' total kills ' + match.group(1)
        match = re.search('(\d+\.\d) (over|under)', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1) + ' ', '')
            formatted_title += ' ' + match.group(1)
        match = re.search('(total kills (.+?))(over|under)', formatted_title)
        if match:
            if match.group(2):
                formatted_title = formatted_title.replace(match.group(1), match.group(2) + 'total kills ')
        return formatted_title

    def _format_first_to_make_number_of_kills(self):
        formatted_title = self.bet_title.lower()
        match = re.search('1st team to .+? (\d+ kills)', formatted_title)
        if match:
            formatted_title = formatted_title.replace(' 1st team to', '')
            formatted_title = formatted_title.replace(' ' + match.group(1), '')
            formatted_title += ' will first make ' + match.group(1)
        return formatted_title

    def _format_first_to_destroy_tower(self):
        formatted_title = self.bet_title.lower()
        if 'destroy first tower' in formatted_title:
            formatted_title = formatted_title.replace(' destroy first tower', '')
            formatted_title += ' will first destroy tower'
        return formatted_title

    def _format_first_to_kill_roshan(self):
        formatted_title = self.bet_title.lower()
        if 'roshan kill' in formatted_title:
            formatted_title = formatted_title.replace(' roshan kill', '')
            formatted_title = formatted_title.replace(' 1st team to', '')
            formatted_title += ' will first kill roshan'
        return formatted_title

    def _format_most_kills(self):
        formatted_title = self.bet_title.lower()
        if 'most kills' in formatted_title:
            if 'equal number' in formatted_title:
                formatted_title = formatted_title.replace('equal number', 'equal')
            else:
                match = re.search(r'(.*)(most kills with handicap(.*)((\+|-)\d*\.\d)) (.*)', formatted_title)
                if match:
                    formatted_title = ''
                    if match.group(1):
                        formatted_title += match.group(1)
                    formatted_title += match.group(6) + ' ' + match.group(2)
                else:
                    formatted_title = formatted_title.replace('most kills ', '')
                    words = re.split(' ', formatted_title)
                    formatted_title = ''
                    for i in range(len(words) ):
                        formatted_title += words[i] + ' '
                    formatted_title += 'most kills'
        return formatted_title

    def _format_draw(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_first_kill(self):
        formatted_title = self.bet_title.lower()
        if 'first blood' in formatted_title:
            formatted_title = formatted_title.replace('1st team to ', '')
            formatted_title = formatted_title.replace(' first blood', '')
            formatted_title += ' first blood'
        return formatted_title

    def _format_map_duration(self):
        formatted_title = self.bet_title.lower()
        if 'map duration' in formatted_title:
            formatted_title = formatted_title.replace('map duration', 'duration')
            formatted_title = formatted_title.replace(' minutes', '')
        return formatted_title


if __name__ == '__main__':
    formatter = MarathonSyntaxFormatter()
    sport = Sport.from_dict(marathon.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\marathon.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)