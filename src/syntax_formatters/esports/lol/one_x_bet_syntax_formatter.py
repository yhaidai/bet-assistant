import re
import os.path

from sport import Sport
from syntax_formatters.esports.lol.abstract_syntax_formatter import AbstractSyntaxFormatter
from syntax_formatters.esports.one_x_bet_syntax_formatter import OneXBetSyntaxFormatter as OSF
from sample_data.lol import one_x_bet


class OneXBetSyntaxFormatter(AbstractSyntaxFormatter, OSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the 1xbet website
    """
    def _format_before(self, sport):
        sport = OSF._format_before(self, sport)
        sport = self._update(sport, self._format_tower)
        sport = self._update(sport, self._format_baron)
        return sport

    def _format_tower(self):
        return self.bet_title.replace('tower', 'turret')

    def _format_baron(self):
        return self.bet_title.replace('nashor', 'baron')

    def _format_first_kill(self):
        formatted_title = self.bet_title.lower()
        if 'first blood - ' in formatted_title:
            formatted_title = formatted_title.replace('first blood - ', '')
            formatted_title += ' first blood'
        return formatted_title

    def _format_specific_kill(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'(next kill (\d+) - )', formatted_title)
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
            # formatted_title = formatted_title.replace('even - no', 'odd')
            # formatted_title = formatted_title.replace('even - yes', 'even')

            found = re.search('total (kills )?(even - yes|even - no)', formatted_title)
            if found:
                formatted_title = formatted_title.replace('even - yes', 'even')
                formatted_title = formatted_title.replace('even - no', 'odd')

            found = re.search(r'total (beaten (dragons|barons)|turrets taken) (over|under) \d+(\.\d)?',
                              formatted_title)
            if found:
                formatted_title = formatted_title.replace('beaten ', '')
                formatted_title = formatted_title.replace('taken ', '')

        found = re.search(r'^(\d map\. )(to|tu) (\d+(\.\d)?) destroyed inhibitors$', formatted_title)
        if found:
            if found.group(2) == 'to':
                spec = 'over '
            else:
                spec = 'under '
            formatted_title = found.group(1) + 'total inhibitors ' + spec + found.group(3)

        found = re.search(r'^(\d map\. )total (over|under) \d+(\.\d)$', formatted_title)
        if found:
            formatted_title = formatted_title.replace('total', 'total kills')

        return formatted_title

    # def _format_handicap(self):
    #     formatted_title = OSF._format_handicap(self)
    #     if 'handicap' in formatted_title and 'maps' not in formatted_title:
    #         formatted_title += ' kills'
    #     return formatted_title

    def _format_first_to_make_number_of_kills(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'^(\d-(st|nd|rd|th) map: )race to (\d+ kills) - w (.+?)$', formatted_title)
        if found:
            formatted_title = found.group(1) + found.group(4) + ' will first make ' + found.group(3)
        return formatted_title

    def _format_first_to_destroy(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'^(\d-(st|nd|rd|th) map: )inhibitor to be destroyed first - w (.+?)$', formatted_title)
        if found:
            formatted_title = found.group(1) + found.group(3) + ' will first destroy inhibitor'

        if '1 turret will be taken by ' in formatted_title:
            formatted_title = formatted_title.replace('1 turret will be taken by ', '')
            formatted_title += ' will first destroy turret'

        return formatted_title

    def _format_first_to_kill(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'^(\d-(st|nd|rd|th) map: )1 (dragon|baron) will be beaten by (.+?)$', formatted_title)
        if found:
            formatted_title = found.group(1) + found.group(4) + ' will first kill ' + found.group(3)
        return formatted_title

    def _format_most_kills(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'^((\d-(st|nd|rd|th) map: )?(.+?)) to perform more kills$', formatted_title)
        if found:
            formatted_title = found.group(1) + ' most kills'
        return formatted_title

    def _format_multikill(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'(.+? )to perform (quadra|penta) kill', formatted_title)
        if found:
            formatted_title = found.group(1) + found.group(2) + ' kill'

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
