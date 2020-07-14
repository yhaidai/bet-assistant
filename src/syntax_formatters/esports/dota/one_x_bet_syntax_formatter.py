import re
import os.path

from Sport import Sport
from syntax_formatters.esports.dota.abstract_syntax_formatter import AbstractSyntaxFormatter
from syntax_formatters.esports.one_x_bet_syntax_formatter import OneXBetSyntaxFormatter as OSF
from sample_data.dota import one_x_bet


class OneXBetSyntaxFormatter(AbstractSyntaxFormatter, OSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the 1xbet website
    """
    def _format_first_to_kill_roshan(self):
        formatted_title = self.bet_title.lower()
        if '1 roshan will be beaten by' in formatted_title:
            formatted_title = formatted_title.replace('1 roshan will be beaten by ', '')
            formatted_title += ' will first kill roshan'
        return formatted_title

    def _format_first_kill(self):
        formatted_title = self.bet_title.lower()
        if 'first blood - ' in formatted_title:
            formatted_title = formatted_title.replace('first blood - ', '')
            formatted_title += ' first blood'
        return formatted_title

    def _format_specific_kill(self):
        formatted_title = self.bet_title.lower()
        match = re.search('(next kill (\d+) - )', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), '')
            formatted_title += ' will make kill ' + match.group(2)
        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'total' in formatted_title:
            formatted_title = formatted_title.replace('total maps. ', '', 1)
            formatted_title = formatted_title.replace('total maps handicap. ', '', 1)
            formatted_title = formatted_title.replace('total maps even/odd. ', '', 1)
            if ' - even' in formatted_title or ' - odd' in formatted_title:
                formatted_title = formatted_title.replace(' -', '', 1)
            match = re.search('total (even|even - no)', formatted_title)
            if match:
                formatted_title = formatted_title.replace('even - no', 'odd')
                formatted_title = formatted_title.replace('total', 'total kills')

            if 'beaten roshans' in formatted_title:
                formatted_title = formatted_title.replace('beaten ', '')

        return formatted_title

    def _format_first_to_destroy_tower(self):
        formatted_title = self.bet_title.lower()
        if '1 tower will be taken by ' in formatted_title:
            formatted_title = formatted_title.replace('1 tower will be taken by ', '')
            formatted_title += ' will first destroy tower'
        return formatted_title


if __name__ == '__main__':
    formatter = OneXBetSyntaxFormatter()
    sport = Sport.from_dict(one_x_bet.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\one_x_bet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
