import re

from syntax_formatters.esports.abstract_syntax_formatter import AbstractSyntaxFormatter
from syntax_formatters.one_x_bet_syntax_formatter import OneXBetSyntaxFormatter as OSF


class OneXBetSyntaxFormatter(AbstractSyntaxFormatter, OSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the 1xbet website
    """
    def _format_before(self, sport):
        """
        Apply unified syntax formatting to the given sport

        :param sport: sport to format
        :type sport: sport
        """
        sport = self._update(sport, self._remove_prefixes)
        sport = self._update(sport, self._format_frags)
        return sport

    def _format_frags(self):
        return self.bet_title.lower().replace('frag', 'kill')

    def _remove_prefixes(self):
        formatted_title = self.bet_title.lower()
        splitter = '. '
        split_title = formatted_title.split(splitter)
        if len(split_title) > 1 and split_title[0] != '1x2':
            formatted_title = formatted_title[len(split_title[0]) + len(splitter):]

        return formatted_title

    def _format_maps(self):
        formatted_title = self.bet_title.lower()
        if 'map' in formatted_title:
            index = formatted_title.find('map') - 1
            map_number = formatted_title[index - 1]
            if map_number == '1':
                ending = '-st'
            elif map_number == '2':
                ending = '-nd'
            elif map_number == '3':
                ending = '-rd'
            elif map_number == '4':
                ending = '-th'
            elif map_number == '5':
                if formatted_title[index - 2] != '.':
                    ending = '-th'
                else:
                    ending = ''
            else:
                ending = ''

            if ending == '':
                formatted_title = formatted_title[:index] + formatted_title[index:]
            else:
                formatted_title = formatted_title[:index] + ending + formatted_title[index:].replace('.', ':', 1)
            # formatted_title = formatted_title.replace('total. ', '', 1)

        return formatted_title

    def _format_correct_score(self):
        return self.bet_title.lower().replace('correct score. ', '', 1).replace(' - yes', '', 1)

    def _format_win(self):
        formatted_title = self.bet_title.lower()
        if '1x2' in formatted_title:
            formatted_title = formatted_title.replace('1x2. ', '', 1)
            formatted_title += ' will win'
        if re.match(r'^.+? wins', formatted_title):
            formatted_title = formatted_title.replace('wins', 'will win')

        return formatted_title

    def _format_handicap(self):
        formatted_title = self.bet_title.lower().replace('handicap. ', '', 1)
        formatted_title = formatted_title.replace('(', '').replace(')', '')
        if 'handicap ' in formatted_title:
            found = re.search(r'^(\d-(st|nd|rd|th) map: )(handicap )(.+? )((\+|-)\d+(\.\d+)?)$', formatted_title)
            if found:
                formatted_title = found.group(1) + found.group(4) + found.group(3) + found.group(5)
            else:
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

    def _format_first_kill(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'^(\d+-(st|nd|rd|th) map: )first kill in (\d+) round - (.+?)$', formatted_title)
        if found:
            formatted_title = found.group(1) + found.group(4) + ' will kill first in round ' + found.group(3)

        return formatted_title

    def _format_win_at_least_number_of_maps(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'^(.+? )to( win at least (.+? )map(s)?)$', formatted_title)
        if found:
            formatted_title = found.group(1) + 'will' + found.group(2)
        found = re.search(r'^(.+? )to( win at least (.+? )map(s)?) - no$',
                          formatted_title)
        if found:
            formatted_title = found.group(1) + 'will not' + found.group(2)

        return formatted_title

    def _format_win_number_of_maps(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'^total won by (.+? )exactly( \d+)$', formatted_title)
        if found:
            formatted_title = found.group(1) + 'will win' + found.group(2) + ' maps'

        return formatted_title

    def _format_total_kills(self):
        formatted_title = self.bet_title.lower()
        found = re.search(r'^(\d+-(st|nd|rd|th) map: )(total kills in )(\d+) round( (over|under) \d+(\.\d+)?)$',
                          formatted_title)
        if found:
            formatted_title = found.group(1) + found.group(3) + 'round ' + found.group(4) + found.group(5)

        return formatted_title
