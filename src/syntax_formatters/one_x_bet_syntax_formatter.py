from pprint import pprint

from abstract_syntax_formatter import AbstractSyntaxFormatter
from scrapers.sample_data import one_x_bet


class OneXBetSyntaxFormatter(AbstractSyntaxFormatter):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the 1xbet website
    """
    _NAME = '1xbet'
    _INVALID_BET_TITLES = ('. ', '')

    def _get_name(self):
        return self._NAME

    def _get_invalid_bet_titles(self):
        return self._INVALID_BET_TITLES

    def _format_other(self, bets):
        """
        Apply unified syntax formatting to the given bets dict

        :param bets: bets dictionary to format
        :type bets: dict
        """
        bets = self._update(bets, self._format_1_2)

        return bets

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
            if ' - even' in formatted_title or ' - odd' in formatted_title:
                formatted_title = formatted_title.replace('-', '—', 1)

            # formatted_title = formatted_title.replace('Total Maps Even/Odd. ', '', 1)
            formatted_title = formatted_title.replace('maps ', '', 1)

        return formatted_title

    def _format_win_in_round(self):
        return self.bet_title.lower().replace('win in round. ', '', 1)

    def _format_team_names(self):
        return self.bet_title.lower().replace('team ', '', 1)

    def _format_correct_score(self):
        return self.bet_title.lower().replace('correct score. ', '', 1).replace(' - yes', '', 1)

    def _format_first_frag(self):
        formatted_title = self.bet_title.lower()
        if 'first frag' in formatted_title:
            formatted_title = formatted_title.replace('-', '—')
            formatted_title = formatted_title.replace('—', '-', 2)

        return formatted_title

    def _format_win(self):
        formatted_title = self.bet_title.lower()
        if '1x2' in formatted_title:
            formatted_title = formatted_title.replace('1x2. ', '', 1)
            formatted_title += ' will win'

        return formatted_title

    def _format_1_2(self):
        formatted_title = self.bet_title.lower()
        try:
            if formatted_title[0] == '1' or '2':
                formatted_title = formatted_title.split('. ')[1]
                formatted_title = formatted_title.replace('team ', '', 1)
        except IndexError:
            pass

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
    formatter = OneXBetSyntaxFormatter()
    formatter.apply_unified_syntax_formatting(one_x_bet.bets)
    pprint(formatter.bets)
