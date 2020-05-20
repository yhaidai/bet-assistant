from pprint import pprint

import one_x_bet


class OneXBetSyntaxFormatter:
    def __init__(self, bets):
        self.bets = {match_title: {} for match_title in bets.keys()}
        self.apply_unified_syntax_formatting(bets)

    def apply_unified_syntax_formatting(self, bets):
        for match_title in bets.keys():
            for bet_title, odds in bets[match_title].items():
                self._format_maps(match_title, bet_title, odds)
                self._format_total(match_title, bet_title, odds)

    def _format_maps(self, match_title, bet_title, odds):
        if 'map' in bet_title:
            index = bet_title.find('map') - 1
            map_number = bet_title[index - 1]
            if map_number == '1':
                ending = '-st'
            elif map_number == '2':
                ending = '-nd'
            else:
                ending = '-rd'

            formatted_title = bet_title[:index] + ending + bet_title[index:].replace('.', ':', 1)
            # formatted_title = formatted_title.replace('Total. ', '', 1)
            formatted_title = formatted_title.lower()

            self.bets[match_title][formatted_title] = odds

    def _format_total(self, match_title, bet_title, odds):
        if 'Total' in bet_title:
            formatted_title = bet_title.replace('Total Maps. ', '', 1)
            formatted_title = formatted_title.replace('Maps ', '', 1)
            formatted_title = formatted_title.lower()

            self.bets[match_title][formatted_title] = odds


formatter = OneXBetSyntaxFormatter(one_x_bet.bets)
pprint(formatter.bets)
