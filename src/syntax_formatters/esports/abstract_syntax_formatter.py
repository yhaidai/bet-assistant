from abc import ABC
from syntax_formatters.abstract_syntax_formatter import AbstractSyntaxFormatter as ASF


class AbstractSyntaxFormatter(ASF, ABC):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the websites
    """

    def apply_unified_syntax_formatting(self, sport):
        """
        Apply unified syntax formatting to the given sport

        :param sport: sport to format
        :type sport: sport
        """
        sport = self._format_before(sport)

        sport = self._update(sport, self._format_maps)
        sport = self._update(sport, self._format_teams)
        sport = self._update(sport, self._format_uncommon_chars)
        sport = self._update(sport, self._format_total)
        sport = self._update(sport, self._format_handicap)
        sport = self._update(sport, self._format_correct_score)
        sport = self._update(sport, self._format_win)
        sport = self._update(sport, self._format_first_kill)
        sport = self._update(sport, self._format_win_at_least_number_of_maps)
        sport = self._update(sport, self._format_win_number_of_maps)
        sport = self._update(sport, self._format_total_kills)

        sport = self._format_after(sport)

        sport = self._format_odds(sport)
        sport = self._format_titles(sport)

        return sport

    def _format_maps(self):
        return self.bet_title.lower()

    def _format_teams(self):
        return self.bet_title.lower()

    def _format_first_kill(self):
        return self.bet_title.lower()

    def _format_win_at_least_number_of_maps(self):
        return self.bet_title.lower()

    def _format_win_number_of_maps(self):
        return self.bet_title.lower()

    def _format_total_kills(self):
        return self.bet_title.lower()

    def _format_multikill(self):
        return self.bet_title.lower()
