from pprint import pprint, pformat
import os.path
import re

from Sport import Sport
from csgo.abstract_syntax_formatter import AbstractSyntaxFormatter
from esports.one_x_bet_syntax_formatter import OneXBetSyntaxFormatter as OSF
from match_title_compiler import MatchTitleCompiler
from sample_data.csgo import one_x_bet


class OneXBetSyntaxFormatter(AbstractSyntaxFormatter, OSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the 1xbet website
    """
    def _format_bomb_exploded(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'^(\d+-(st|nd|rd|th) map: bomb exploded in )(\d+)( )(round)$', formatted_title)
        if match:
            formatted_title = match.group(1) + match.group(5) + match.group(4) + match.group(3)
        match = re.search(r'^(\d+-(st|nd|rd|th) map: bomb defused in round \d+)$', formatted_title)
        if match:
            formatted_title = match.group(1)

        return formatted_title

    def _format_bomb_planted(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'^(\d+-(st|nd|rd|th) map: bomb )(planted in round \d+) - no$', formatted_title)
        if match:
            formatted_title = match.group(1) + 'not ' + match.group(3)

        return formatted_title

    def _format_overtime(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'^(\d+-(st|nd|rd|th) map: )will there be (overtime)\?( - no)?$', formatted_title)
        if match:
            if match.group(4):
                formatted_title = match.group(1) + match.group(3) + match.group(4)
                formatted_title = formatted_title.replace(' -', ' —', 1)
            else:
                formatted_title = match.group(1) + match.group(3) + ' — yes'

        return formatted_title

    def _format_individual_total_rounds(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'^(\d+-(st|nd|rd|th) map: )individual total (\d+)(( over| under)( \d+(\.\d+)?))$',
                          formatted_title)
        if match:
            teams = MatchTitleCompiler.decompile_match_title(self.match_title)
            if match.group(3) == '1':
                team = teams[0]
            else:
                team = teams[1]
            formatted_title = match.group(1) + team + ' total' + match.group(4)

        return formatted_title


if __name__ == '__main__':
    formatter = OneXBetSyntaxFormatter()
    sport = Sport.from_dict(one_x_bet.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\parimatch.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
