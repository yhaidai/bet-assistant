from pprint import pprint

from abstract_syntax_formatter import AbstractSyntaxFormatter
from scrapers.sample_data import one_x_bet


class OneXBetSyntaxFormatter(AbstractSyntaxFormatter):
    def __init__(self, bets):
        super().__init__(bets)

    def apply_unified_syntax_formatting(self, bets):
        bets = self._update(bets, self._format_maps)
        bets = self._update(bets, self._format_total)
        bets = self._update(bets, self._format_handicap)
        bets = self._update(bets, self._format_win_in_round)
        bets = self._update(bets, self._format_team)
        bets = self._update(bets, self._format_correct_score)
        bets = self._update(bets, self._format_1x2)
        bets = self._update(bets, self._format_uncommon_chars)

    def _format_maps(self):
        formatted_title = self.bet_title.lower()

        if 'map' in self.bet_title:
            index = formatted_title.find('map') - 1
            map_number = formatted_title[index - 1]
            if map_number == '1':
                ending = '-st'
            elif map_number == '2':
                ending = '-nd'
            else:
                ending = '-rd'

            formatted_title = formatted_title[:index] + ending + formatted_title[index:].replace('.', ':', 1)
            formatted_title = formatted_title.replace('total. ', '', 1)

        return formatted_title

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'total' in formatted_title:
            formatted_title = formatted_title.replace('total maps. ', '', 1)
            formatted_title = formatted_title.replace('total maps handicap. ', '', 1)
            formatted_title = formatted_title.replace('total maps even/odd. ', '', 1)

            # formatted_title = formatted_title.replace('Total Maps Even/Odd. ', '', 1)
            formatted_title = formatted_title.replace('maps ', '', 1)

        return formatted_title

    def _format_win_in_round(self):
        return self.bet_title.lower().replace('win in round. ', '', 1)

    def _format_team(self):
        return self.bet_title.lower().replace('team ', '', 1)

    def _format_correct_score(self):
        return self.bet_title.lower().replace('correct score. ', '', 1).replace(' - yes', '', 1)

    def _format_1x2(self):
        formatted_title = self.bet_title.lower()
        if '1x2' in formatted_title:
            formatted_title = formatted_title.replace('1x2. ', '', 1)
            formatted_title += ' will win'

        return formatted_title

    def _format_handicap(self):
        formatted_title = self.bet_title.lower().replace('handicap. ', '', 1)
        formatted_title = formatted_title.replace('(', '').replace(')', '')
        if 'handicap ' in formatted_title:
            sign_index = formatted_title.find('handicap ') + len('handicap ')
            if formatted_title[sign_index] != '-':
                formatted_title = formatted_title.replace('handicap ', 'handicap +', 1)

        return formatted_title

    def _format_uncommon_chars(self):
        formatted_title = self.bet_title.lower()

        # these are different characters :)
        formatted_title = formatted_title.replace('с', 'c')
        formatted_title = formatted_title.replace('–', '-')

        return formatted_title


if __name__ == '__main__':
    formatter = OneXBetSyntaxFormatter(one_x_bet.bets)
    pprint(formatter.bets)
