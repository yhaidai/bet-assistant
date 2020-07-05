import unittest
import re

from sample_data.csgo.parimatch import bets as parimatch_bets
from sample_data.csgo.one_x_bet import bets as one_x_bet_bets
from sample_data.csgo.ggbet import bets as ggbet_bets
from sample_data.csgo.favorit import bets as favorit_bets
from sample_data.csgo.marathon import bets as marathon_bets
from csgo.parimatch_syntax_formatter import ParimatchSyntaxFormatter
from csgo.one_x_bet_syntax_formatter import OneXBetSyntaxFormatter
from csgo.ggbet_syntax_formatter import GGBetSyntaxFormatter
from csgo.favorit_syntax_formatter import FavoritSyntaxFormatter
from csgo.marathon_syntax_formatter import MarathonSyntaxFormatter


class TestSyntaxFormatters(unittest.TestCase):
    def setUp(self) -> None:
        self.parimatch_bets = parimatch_bets
        self.one_x_bet_bets = one_x_bet_bets
        self.ggbet_bets = ggbet_bets
        self.favorit_bets = favorit_bets
        self.marathon_bets = marathon_bets

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
            r'^(\d+-(st|nd|rd|th) map: )?(.+? )?total (kills in round \d+ )?(over|under) (\d+(\.\d)?)( maps)?$',
            r'^(\d+-(st|nd|rd|th) map: )?total( maps)? — (even|odd)$',  # total even/odd
            r'^(\d+-(st|nd|rd|th) map: )?handicap (.+? )(\+|-)?\d+(\.\d)?$',  # rounds handicap
            r'^(.+? )handicap (\+|-)\d+(\.\d)? maps$',  # maps handicap
            r'^(.+?) will kill first in round \d+$',  # first frag in round
            r'^(.+?) will be first to win \d+ rounds$',  # first frag in round
            r'^(\d+-(st|nd|rd|th) map: )overtime — (yes|no)$',  # overtime yes/no
            r'^(\d+-(st|nd|rd|th) map: )bomb (exploded|defused) in round \d+$',  # bomb exploded/defused
            r'^(\d+-(st|nd|rd|th) map: )bomb (planted|not planted) in round \d+$',  # bomb planted/not planted
            ]
        self.odds_value_pattern = r'^\d+(\.\d+)?$'
        self.bookmaker_info_pattern = r'^[a-z0-9]+?\(https://.+?\)$'

    # @unittest.skip
    def test_parimatch_unified_syntax_formatting(self):
        bets = self.parimatch_syntax_formatter.apply_unified_syntax_formatting(self.parimatch_bets)
        self._test_unified_syntax_formatting(bets)

    # @unittest.skip
    def test_one_x_bet_unified_syntax_formatting(self):
        bets = self.one_x_bet_syntax_formatter.apply_unified_syntax_formatting(self.one_x_bet_bets)
        self._test_unified_syntax_formatting(bets)

    # @unittest.skip
    def test_ggbet_unified_syntax_formatting(self):
        bets = self.ggbet_syntax_formatter.apply_unified_syntax_formatting(self.ggbet_bets)
        self._test_unified_syntax_formatting(bets)

    # @unittest.skip
    def test_favorit_unified_syntax_formatting(self):
        bets = self.favorit_syntax_formatter.apply_unified_syntax_formatting(self.favorit_bets)
        self._test_unified_syntax_formatting(bets)

    # @unittest.skip
    def test_marathon_unified_syntax_formatting(self):
        bets = self.marathon_syntax_formatter.apply_unified_syntax_formatting(self.marathon_bets)
        self._test_unified_syntax_formatting(bets)

    def _test_unified_syntax_formatting(self, bets):
        self.assertIs(type(bets), dict, 'apply_unified_syntax_formatting() must return dict')

        for match_title in bets:
            self.assertIs(type(bets[match_title]), dict, 'bets[match_title] must be dict')

            with self.subTest(match_title=match_title):
                self.assertRegex(match_title, self.match_title_pattern, 'match title must match its pattern')

                for bet_title, odds in bets[match_title].items():
                    self.assertIs(type(odds), dict, 'bets[match_title][bet_title] must be dict')

                    with self.subTest(bet_title=bet_title, odds=odds):
                        if not re.match('|'.join(self.bet_title_patterns), bet_title):
                            print(bet_title)
                        # self.assertRegex(bet_title, '|'.join(self.bet_title_patterns),
                        #                  'bet title must match its pattern')

                        self.assertEqual(len(odds.keys()), 1, 'bet can\'t have multiple odds')
                        self.assertEqual(len(odds.values()), 1, 'bet can\'t have multiple bookmakers/urls')
                        for odds_value, bookmaker_info in odds.items():
                            self.assertIs(type(odds_value), str, 'bets[match_title][bet_title] keys must be str')
                            self.assertIs(type(bookmaker_info), str, 'bets[match_title][bet_title] values must be str')
                            self.assertRegex(odds_value, self.odds_value_pattern, 'odds must match their pattern')
                            self.assertRegex(bookmaker_info, self.bookmaker_info_pattern,
                                             'bookmaker info must match its pattern')


if __name__ == '__main__':
    unittest.main()
