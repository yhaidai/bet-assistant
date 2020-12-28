from syntax_formatters.esports.esports_abstract_syntax_formatter import EsportsAbstractSyntaxFormatter
from syntax_formatters.parimatch_syntax_formatter import ParimatchSyntaxFormatter as PSF
from match_title_compiler import MatchTitleCompiler


class EsportsParimatchSyntaxFormatter(EsportsAbstractSyntaxFormatter, PSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the parimatch website
    """
    @staticmethod
    def _swap_substrings(text, pattern, id1, id2, separator):
        substrings = text.split(pattern)
        try:
            temp = substrings[id1]
        except IndexError:
            print(substrings)
            raise IndexError
        substrings[id1] = substrings[id2]
        substrings[id2] = temp

        result = ''
        for s in substrings:
            result += s + separator

        tail_length = len(separator)
        if tail_length > 0:
            result = result[:-tail_length]

        return result

    def _format_win(self):
        formatted_title = self.bet_title.lower()
        teams = self.match_title.get_teams()

        if 'win of' in formatted_title:
            formatted_title = formatted_title.replace(' team', '')
            if formatted_title.find('1st') != -1:
                team_number = '1st'
                team = teams[0]
            elif formatted_title.find('2nd') != -1:
                team_number = '2nd'
                team = teams[1]
            else:
                raise NotImplementedError('Not "1st" nor "2nd" was found')
            to_be_replaced = 'win of the ' + team_number
            formatted_title = formatted_title.replace(to_be_replaced, team + ' will win', 1)
        elif 'home win' in formatted_title:
            formatted_title = formatted_title.replace('home', teams[0] + ' will')
        elif 'away win' in formatted_title:
            formatted_title = formatted_title.replace('away', teams[1] + ' will')
        elif 'draw' in formatted_title:
            formatted_title += ' will win'

        return formatted_title

    def _format_uncommon_chars(self):
        formatted_title = self.bet_title.lower()
        formatted_title = formatted_title.replace('–', '-')

        return formatted_title
