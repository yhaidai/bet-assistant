import unittest
import re

from sport import Sport
from sample_data.lol.parimatch import sport as parimatch_lol_dict
from sample_data.lol.one_x_bet import sport as one_x_bet_lol_dict
from sample_data.lol.ggbet import sport as ggbet_lol_dict
from sample_data.lol.favorit import sport as favorit_lol_dict
from sample_data.lol.marathon import sport as marathon_lol_dict
from syntax_formatters.esports.lol.parimatch_syntax_formatter import ParimatchSyntaxFormatter
from syntax_formatters.esports.lol.one_x_bet_syntax_formatter import OneXBetSyntaxFormatter
from syntax_formatters.esports.lol.ggbet_syntax_formatter import GGBetSyntaxFormatter
from syntax_formatters.esports.lol.favorit_syntax_formatter import FavoritSyntaxFormatter
from syntax_formatters.esports.lol.marathon_syntax_formatter import MarathonSyntaxFormatter


class TestSyntaxFormatters(unittest.TestCase):
    def setUp(self) -> None:
        self.parimatch_lol_dict = parimatch_lol_dict
        self.one_x_bet_lol_dict = one_x_bet_lol_dict
        self.ggbet_lol_dict = ggbet_lol_dict
        self.favorit_lol_dict = favorit_lol_dict
        self.marathon_lol_dict = marathon_lol_dict

        self.parimatch_syntax_formatter = ParimatchSyntaxFormatter()
        self.one_x_bet_syntax_formatter = OneXBetSyntaxFormatter()
        self.ggbet_syntax_formatter = GGBetSyntaxFormatter()
        self.favorit_syntax_formatter = FavoritSyntaxFormatter()
        self.marathon_syntax_formatter = MarathonSyntaxFormatter()

        self.bet_title_patterns = [
            r'^(\d+-(st|nd|rd|th) map: )?(.+?) will (win|lose)$',  # win
            r'^(.+? )?will (not )?win at least .+? map(s)?$',  # win at least number of maps
            r'^(\d+-(st|nd|rd|th) map: )?correct score \d+-\d+$',  # correct score
            # total over/under
            r'^(\d+-(st|nd|rd|th) map: )?(.+? )?total ((maps|kills|barons|dragons|turrets|inhibitors) )(over|under) ('
            r'\d+(\.\d)?)$',
            r'^(\d+-(st|nd|rd|th) map: )?total( (maps|kills)) (even|odd)$',  # total even/odd
            r'^(\d+-(st|nd|rd|th) map: )?(.+? )handicap (\+|-)\d+(\.\d)? kills$',  # kills handicap
            r'^(.+? )handicap (\+|-)\d+(\.\d)? maps$',  # maps handicap
            r'^\d+-(st|nd|rd|th) map: duration (over|under) \d+(\.\d)?$',  # map duration
            r'^\d+-(st|nd|rd|th) map: (.+?) will make kill \d+$',  # kill number
            # first to
            r'^\d+-(st|nd|rd|th) map: (.+?) will first (kill (nashor|dragon|baron)|destroy (turret|inhibitor))$',
            r'^\d+-(st|nd|rd|th) map: (.+?) will first make \d+ kills$',
            r'^(.+?) first blood$',  # first blood
            r'^(\d+-(st|nd|rd|th) map: )?(.+?) most kills$',  # most kills
            r'^.+? (quadra|penta) kill'
            ]
        self.odds_pattern = r'^\d+(\.\d+)?$'

    # @unittest.skip
    def test_parimatch_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.parimatch_lol_dict)
        sport = self.parimatch_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_one_x_bet_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.one_x_bet_lol_dict)
        sport = self.one_x_bet_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_ggbet_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.ggbet_lol_dict)
        sport = self.ggbet_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_favorit_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.favorit_lol_dict)
        sport = self.favorit_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_marathon_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.marathon_lol_dict)
        sport = self.marathon_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    def _test_unified_syntax_formatting(self, sport):
        for match in sport:
            with self.subTest(match_title=match.title):
                for bet in match:
                    with self.subTest(bet_title=bet.title, odds=bet.odds):
                        if not re.match('|'.join(self.bet_title_patterns), bet.title):
                            print(bet.bookmaker + ': ' + bet.title)
                        self.assertRegex(bet.title, '|'.join(self.bet_title_patterns),
                                         'bet title must match its pattern')
                        self.assertRegex(bet.odds, self.odds_pattern, 'odds must match their pattern')


if __name__ == '__main__':
    unittest.main()
