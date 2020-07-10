import os.path
import re

from Sport import Sport
from syntax_formatters.esports.csgo.abstract_syntax_formatter import AbstractSyntaxFormatter
from esports.parimatch_syntax_formatter import ParimatchSyntaxFormatter as PSF
from sample_data.csgo import parimatch


class ParimatchSyntaxFormatter(AbstractSyntaxFormatter, PSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the parimatch website
    """
    def _format_handicap(self):
        formatted_title = self.bet_title.lower()

        if 'handicap' in formatted_title:
            formatted_title = self._swap_substrings(formatted_title, '. ', 1, 2, '')
            formatted_title = formatted_title.replace('handicap value', '', 1).replace('coefficient', '', 1)

            if 'map:' in formatted_title:
                # cut 'handicap ' out
                formatted_title = formatted_title.replace('handicap ', '', 1)

                # remove prefix
                prefix = formatted_title[:formatted_title.find(':') + 2]
                formatted_title = formatted_title.replace(prefix, '', 1)

                # insert 'handicap '
                formatted_title = prefix + 'handicap ' + formatted_title
            else:
                formatted_title += ' maps'

        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'total' in formatted_title:
            formatted_title = self._swap_substrings(formatted_title, '. ', 1, 2, ' ')

        return formatted_title

    def _format_after(self, bets):
        bets = self._update(bets, self._fix_total_maps)
        return bets

    def _fix_total_maps(self):
        # Если захочешь, перепишешь по-другому, мне было проще так, вдруг мы потом решим опять менять вид total maps
        formatted_title = self.bet_title.lower()
        match = re.search('^total — (even|odd)', formatted_title)
        if match:
            formatted_title = formatted_title.replace('total', 'total maps')

        match = re.search('^total (over|under)', formatted_title)
        if match:
            formatted_title += ' maps'
        return formatted_title


if __name__ == '__main__':
    formatter = ParimatchSyntaxFormatter()
    sport = Sport.from_dict(parimatch.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\parimatch.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
