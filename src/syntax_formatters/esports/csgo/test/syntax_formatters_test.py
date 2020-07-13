import unittest
import re

from Sport import Sport
from sample_data.csgo.parimatch import sport as parimatch_csgo_dict
from sample_data.csgo.one_x_bet import sport as one_x_bet_csgo_dict
from sample_data.csgo.ggbet import sport as ggbet_csgo_dict
from sample_data.csgo.favorit import sport as favorit_csgo_dict
from sample_data.csgo.marathon import sport as marathon_csgo_dict
from syntax_formatters.esports.csgo.parimatch_syntax_formatter import ParimatchSyntaxFormatter
from syntax_formatters.esports.csgo.one_x_bet_syntax_formatter import OneXBetSyntaxFormatter
from syntax_formatters.esports.csgo.ggbet_syntax_formatter import GGBetSyntaxFormatter
from syntax_formatters.esports.csgo.favorit_syntax_formatter import FavoritSyntaxFormatter
from syntax_formatters.esports.csgo.marathon_syntax_formatter import MarathonSyntaxFormatter


class TestSyntaxFormatters(unittest.TestCase):
    def setUp(self) -> None:
        self.parimatch_csgo_dict = parimatch_csgo_dict
        self.one_x_bet_csgo_dict = one_x_bet_csgo_dict
        self.ggbet_csgo_dict = ggbet_csgo_dict
        self.favorit_csgo_dict = favorit_csgo_dict
        self.marathon_csgo_dict = marathon_csgo_dict

        self.parimatch_syntax_formatter = ParimatchSyntaxFormatter()
        self.one_x_bet_syntax_formatter = OneXBetSyntaxFormatter()
        self.ggbet_syntax_formatter = GGBetSyntaxFormatter()
        self.favorit_syntax_formatter = FavoritSyntaxFormatter()
        self.marathon_syntax_formatter = MarathonSyntaxFormatter()

        self.match_title_pattern = '^[a-z0-9]+( - [a-z0-9]+)?'
        self.bet_title_patterns = [
            r'^(\d+-(st|nd|rd|th) map: )?(.+? )?will (not )?win( in round \d+| (at least )?.+? map(s)?)?$',  # win
            r'^(\d+-(st|nd|rd|th) map: )?correct score \d+-\d+$',  # correct score
            # total over/under
            r'^(\d+-(st|nd|rd|th) map: )?(.+? )?total ((maps|rounds|kills in round \d+) )?(over|under) (\d+(\.\d)?)$',
            r'^(\d+-(st|nd|rd|th) map: )?total( (maps|rounds))? (even|odd)$',  # total even/odd
            r'^(\d+-(st|nd|rd|th) map: )?(.+? )handicap (\+|-)\d+(\.\d)? rounds$',  # rounds handicap
            r'^(.+? )handicap (\+|-)\d+(\.\d)? maps$',  # maps handicap
            r'^(.+?) will kill first in round \d+$',  # first frag in round
            r'^(.+?) will be first to win \d+ rounds$',  # first frag in round
            r'^(\d+-(st|nd|rd|th) map: )overtime (yes|no)$',  # overtime yes/no
            r'^(\d+-(st|nd|rd|th) map: )bomb (exploded|defused) in round \d+$',  # bomb exploded/defused
            r'^(\d+-(st|nd|rd|th) map: )bomb (planted|not planted) in round \d+$',  # bomb planted/not planted
            ]
        self.odds_pattern = r'^\d+(\.\d+)?$'

    # @unittest.skip
    def test_parimatch_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.parimatch_csgo_dict)
        sport = self.parimatch_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_one_x_bet_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.one_x_bet_csgo_dict)
        sport = self.one_x_bet_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_ggbet_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.ggbet_csgo_dict)
        sport = self.ggbet_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_favorit_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.favorit_csgo_dict)
        sport = self.favorit_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_marathon_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.marathon_csgo_dict)
        sport = self.marathon_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    def _test_unified_syntax_formatting(self, sport):
        for match in sport:
            with self.subTest(match_title=match.title):
                # print(match.title)
                self.assertRegex(match.title, self.match_title_pattern, 'match title must match its pattern')

                for bet in match:
                    with self.subTest(bet_title=bet.title, odds=bet.odds):
                        if not re.match('|'.join(self.bet_title_patterns), bet.title):
                            print(bet.title)
                        self.assertRegex(bet.title, '|'.join(self.bet_title_patterns),
                                         'bet title must match its pattern')
                        self.assertRegex(bet.odds, self.odds_pattern, 'odds must match their pattern')


if __name__ == '__main__':
    unittest.main()
