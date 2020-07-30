import re
from abc import ABC, abstractmethod

from match import Match
from sport import Sport


class AbstractSyntaxFormatter(ABC):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the websites
    """
    def format_match(self, match):
        match = self.apply_unified_syntax_formatting(Sport('', [match])).matches[0]
        self._format_bet_titles_teams(match)
        return match

    @staticmethod
    def _format_bet_titles_teams(match: Match) -> None:
        try:
            for bet in match:
                for raw_team, unified_team in match.title.similarities.items():
                    # if raw_team != unified_team:
                    # print('Changing ' + raw_team + ' to ' + unified_team)
                    bet.title = bet.title.replace(raw_team, unified_team)
        except AttributeError:
            return

    def apply_unified_syntax_formatting(self, sport: Sport):
        """
        Apply unified syntax formatting to the given sport

        :param sport: sport to format
        :type sport: sport
        """
        sport = self._format_before(sport)

        sport = self._update(sport, self._format_uncommon_chars)
        sport = self._update(sport, self._format_total)
        sport = self._update(sport, self._format_handicap)
        sport = self._update(sport, self._format_correct_score)
        sport = self._update(sport, self._format_win)

        sport = self._format_after(sport)

        sport = self._format_odds(sport)
        # sport = self._format_titles(sport)

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

    # def _format_titles(self, sport):
    #     """
    #     Remove specific words from titles
    #
    #     :param sport: sport to format
    #     :type sport: sport
    #     :return: updated sport
    #     :rtype: sport
    #     """
    #     sport = self._format_match_titles(sport)
    #     sport = self._format_bet_titles(sport)
    #
    #     return sport
    #
    # def _format_bet_titles(self, sport):
    #     """
    #     Remove specific words from bet titles
    #
    #     :param sport: sport to format
    #     :type sport: sport
    #     :return: updated sport
    #     :rtype: sport
    #     """
    #     for match in sport:
    #         for bet in match:
    #             for pattern in self._REMOVE_FROM_TITLES:
    #                 bet.title = re.sub(pattern, '', bet.title)
    #
    #     return sport
    #
    # def _format_match_titles(self, sport):
    #     """
    #     Remove specific words from match titles
    #
    #     :param sport: sport to format
    #     :type sport: sport
    #     :return: updated sport
    #     :rtype: sport
    #     """
    #     for match in sport:
    #         teams = MatchTitleCompiler.decompile_match_title(match.title)
    #         formatted_match_title = MatchTitleCompiler.compile_match_title(*teams[:2], sort=True)
    #         swapped = formatted_match_title != match.title
    #
    #         for word in self._REMOVE_FROM_TITLES:
    #             formatted_match_title = formatted_match_title.replace(word, '')
    #
    #         if swapped:
    #             for bet in match:
    #                 found = re.search(r'^((\d+-(st|nd|rd|th) map: )?correct score )(\d+)-(\d+)$', bet.title)
    #                 if found:
    #                     formatted_bet_title = found.group(1) + found.group(5) + '-' + found.group(4)
    #                     bet.title = formatted_bet_title
    #
    #         match.title = formatted_match_title
    #
    #     return sport

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
                if not bet.title:
                    print('Odds: ', bet.odds, ';')
                assert type(bet.odds) == str
                if bet.odds == '':
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

    def swap_teams(self, title):
        teams = self.match_title.raw_teams
        if teams[0] in title:
            title = title.replace(teams[0], teams[1])
        else:
            title = title.replace(teams[1], teams[0])
        return title

    def _move_teams_left(self, formatted_title=None):
        if not formatted_title:
            formatted_title = self.bet_title.lower()
        try:
            teams = self.match_title.raw_teams
        except AttributeError:
            teams = self.match_title.teams

        for team in teams:
            if team in formatted_title:
                match = re.search(r'^' + team, formatted_title)
                if match:
                    break
                formatted_title = formatted_title.replace(' ' + team, '')
                match = re.search(r'(\d+-(st|nd|rd|th) (map:|half))', formatted_title)
                if match:
                    formatted_title = formatted_title.replace(match.group(1), match.group(1) + ' ' + team)
                else:
                    formatted_title = team + ' ' + formatted_title
                break

        return formatted_title
