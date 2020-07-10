import re
from abc import ABC, abstractmethod

from match_title_compiler import MatchTitleCompiler


class AbstractSyntaxFormatter(ABC):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the websites
    """
    _REMOVE_FROM_TITLES = ['team ', ' team', ' esports', ' club', ' gaming']

    def apply_unified_syntax_formatting(self, sport):
        """
        Apply unified syntax formatting to the given sport

        :param sport: sport to format
        :type sport: Sport
        """
        sport = self._format_before(sport)

        sport = self._update(sport, self._format_total)
        sport = self._update(sport, self._format_handicap)
        sport = self._update(sport, self._format_correct_score)
        sport = self._update(sport, self._format_win)
        sport = self._update(sport, self._format_uncommon_chars)

        sport = self._format_after(sport)

        sport = self._format_odds(sport)
        sport = self._format_titles(sport)

        return sport

    def _format_before(self, sport):
        """
        Apply unified syntax formatting to the given bets dict before obligatory updates are run. Subclass specific

        :param sport: sport to format
        :type sport: Sport
        :return: formatted sport
        :rtype: Sport
        """
        return sport

    def _format_after(self, sport):
        """
        Apply unified syntax formatting to the given bets dict after obligatory updates are run. Subclass specific

        :param sport: sport to format
        :type sport: Sport
        :return: formatted sport
        :rtype: Sport
        """
        return sport

    @abstractmethod
    def _get_name(self):
        pass

    def _get_invalid_bet_titles(self):
        return ()

    def _get_invalid_match_titles(self):
        return ()

    def _update(self, sport, _callable):
        """
        Update self.bets and given bets dictionaries according to _callable method

        :param sport: bets dictionary to format
        :type sport: Sport
        :param _callable: method to be called to get formatted bet title
        :type _callable: method
        :return: updated sport
        :rtype: Sport
        """
        invalid_bet_titles = self._get_invalid_bet_titles()
        invalid_match_titles = self._get_invalid_match_titles()

        for match in list(sport):
            self.match_title = match.title
            for bet in list(match):
                self.bet_title = bet.title
                formatted_title = _callable()
                bet.title = formatted_title

                if self.bet_title in invalid_bet_titles:
                    match.bets.remove(bet)

            if self.match_title in invalid_match_titles:
                sport.matches.remove(match)

        return sport

    def _format_titles(self, sport):
        """
        Remove specific words from titles

        :param sport: sport to format
        :type sport: Sport
        :return: updated sport
        :rtype: Sport
        """
        sport = self._format_match_titles(sport)
        sport = self._format_bet_titles(sport)

        return sport

    def _format_bet_titles(self, sport):
        """
        Remove specific words from bet titles

        :param sport: sport to format
        :type sport: Sport
        :return: updated sport
        :rtype: Sport
        """
        for match in sport:
            for bet in match:
                for word in self._REMOVE_FROM_TITLES:
                    bet.title = bet.title.replace(word, '')

        return sport

    def _format_match_titles(self, sport):
        """
        Remove specific words from match titles

        :param sport: sport to format
        :type sport: Sport
        :return: updated sport
        :rtype: Sport
        """
        for match in sport:
            teams = MatchTitleCompiler.decompile_match_title(match.title)
            formatted_match_title = MatchTitleCompiler.compile_match_title(*teams, sort=True)
            swapped = formatted_match_title != match.title

            for word in self._REMOVE_FROM_TITLES:
                formatted_match_title = formatted_match_title.replace(word, '')

            if swapped:
                for bet in match:
                    found = re.search(r'^((\d+-(st|nd|rd|th) map: )?correct score )(\d+)-(\d+)$', bet.title)
                    if found:
                        formatted_bet_title = found.group(1) + found.group(5) + '-' + found.group(4)
                        bet.title = formatted_bet_title

            match.title = formatted_match_title

        return sport

    @staticmethod
    def _format_odds(sport):
        """
        Remove empty odds bet titles

        :param sport: sport to format
        :type sport: Sport
        :return: updated sport
        :rtype: Sport
        """
        for match in sport:
            for bet in list(match):
                if not bet.odds:
                    match.bets.remove(bet)

        return sport

    def _format_win(self):
        return self.bet_title.lower()

    def _format_total(self):
        return self.bet_title.lower()

    def _format_handicap(self):
        return self.bet_title.lower()

    def _format_correct_score(self):
        return self.bet_title.lower()

    def _format_uncommon_chars(self):
        return self.bet_title.lower()
