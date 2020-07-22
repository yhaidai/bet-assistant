import os.path
import re

from sport import Sport
from syntax_formatters.esports.csgo.csgo_abstract_syntax_formatter import CSGOAbstractSyntaxFormatter
from esports.esports_one_x_bet_syntax_formatter import EsportsOneXBetSyntaxFormatter as OSF
from match_title_compiler import MatchTitleCompiler
from sample_data.csgo import one_x_bet


class CSGOOneXBetSyntaxFormatter(CSGOAbstractSyntaxFormatter, OSF):
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
                # formatted_title = formatted_title.replace(' -', ' —', 1)
                formatted_title = formatted_title.replace(' -', '', 1)
            else:
                # formatted_title = match.group(1) + match.group(3) + ' — yes'
                formatted_title = match.group(1) + match.group(3) + ' yes'
        return formatted_title

    def _format_individual_total_rounds(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'^(\d+-(st|nd|rd|th) map: )individual total (\d+)(( over| under)( \d+(\.\d+)?))$',
                          formatted_title)
        if match:
            teams = self.match_title.teams
            if match.group(3) == '1':
                team = teams[0]
            else:
                team = teams[1]
            formatted_title = match.group(1) + team + ' total' + match.group(4)

        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'total' in formatted_title:
            formatted_title = formatted_title.replace('total maps. ', '', 1)
            formatted_title = formatted_title.replace('total maps handicap. ', '', 1)
            formatted_title = formatted_title.replace('total maps even/odd. ', '', 1)
            if ' - even' in formatted_title or ' - odd' in formatted_title:
                formatted_title = formatted_title.replace('- ', '', 1)
        return formatted_title

    def _format_after(self, bets):
        bets = self._update(bets, self._fix_t_ct_and_total_rounds)
        return bets

    def _fix_t_ct_and_total_rounds(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'(counter )?(terrorists)( -)', formatted_title)
        if match:
            formatted_title = formatted_title.replace('counter ', 'c')
            formatted_title = formatted_title.replace('terrorists', 't')
            formatted_title = formatted_title.replace(' -', '')
        found = re.search(r'^\d-(st|nd|rd|th) map: (.+? )?total (over|under) \d+(\.\d)', formatted_title)
        if found:
            formatted_title = formatted_title.replace('total', 'total rounds')
        return formatted_title

    def _format_handicap(self):
        formatted_title = OSF._format_handicap(self)
        if 'handicap' in formatted_title and ' maps' not in formatted_title:
            formatted_title += ' rounds'

        return formatted_title


if __name__ == '__main__':
    formatter = CSGOOneXBetSyntaxFormatter()
    sport = Sport.from_dict(one_x_bet.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\one_x_bet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
