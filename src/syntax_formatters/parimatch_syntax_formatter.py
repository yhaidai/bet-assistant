from pprint import pprint

from abstract_syntax_formatter import AbstractSyntaxFormatter
from scrapers.sample_data import parimatch
from syntax_formatter import SyntaxFormatter


class ParimatchSyntaxFormatter(AbstractSyntaxFormatter):
    def __init__(self, bets):
        super().__init__(bets)

    def apply_unified_syntax_formatting(self, bets):
        bets = self._update(bets, self._format_total)
        bets = self._update(bets, self._format_win_of)
        bets = self._update(bets, self._format_handicap)
        bets = self._update(bets, self._format_uncommon_chars)

    @staticmethod
    def _swap_substrings(text, pattern, id1, id2, separator):
        substrings = text.split(pattern)
        temp = substrings[id1]
        substrings[id1] = substrings[id2]
        substrings[id2] = temp

        result = ''
        for s in substrings:
            result += s + separator

        tail_length = len(separator)
        if tail_length > 0:
            result = result[:-tail_length]

        return result

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'total' in formatted_title:
            formatted_title = self._swap_substrings(formatted_title, '. ', 1, 2, ' ')

        return formatted_title

    def _format_win_of(self):
        formatted_title = self.bet_title.lower()
        team_name = ''
        team_number = ''

        if 'win of' in formatted_title:
            if formatted_title.find('1st') != -1:
                team_number = '1st'
                team_name = SyntaxFormatter.decompile_match_title(self.match_title)[0]
            elif formatted_title.find('2nd') != -1:
                team_number = '2nd'
                team_name = SyntaxFormatter.decompile_match_title(self.match_title)[1]
            else:
                raise NotImplementedError('Not "1st" nor "2nd" was found')

        to_be_replaced = 'win of the ' + team_number + ' team'
        formatted_title = formatted_title.replace(to_be_replaced, team_name + ' will win', 1)

        return formatted_title

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

    def _format_uncommon_chars(self):
        formatted_title = self.bet_title.lower()

        # these are different characters :)
        formatted_title = formatted_title.replace('–', '-')

        return formatted_title


if __name__ == '__main__':
    formatter = ParimatchSyntaxFormatter(parimatch.bets)
    pprint(formatter.bets)
