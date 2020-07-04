import re
from abc import ABC, abstractmethod

from abstract_scraper import AbstractScraper
from match_title_compiler import MatchTitleCompiler


class AbstractSyntaxFormatter(ABC):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the websites
    """
    _REMOVE_FROM_TITLES = ['team ', ' team', ' esports', ' club']

    def __init__(self):
        self.bets = {}

    def apply_unified_syntax_formatting(self, bets):
        """
        Apply unified syntax formatting to the given bets dict

        :param bets: bets dictionary to format
        :type bets: dict
        """
        self.bets = bets.copy()

        bets = self._format_before(bets)

        bets = self._update(bets, self._format_total)
        bets = self._update(bets, self._format_maps)
        bets = self._update(bets, self._format_handicap)
        bets = self._update(bets, self._format_win_in_round)
        bets = self._update(bets, self._format_team_names)
        bets = self._update(bets, self._format_correct_score)
        bets = self._update(bets, self._format_win)
        bets = self._update(bets, self._format_uncommon_chars)
        bets = self._update(bets, self._format_bomb_exploded)
        bets = self._update(bets, self._format_bomb_planted)
        bets = self._update(bets, self._format_overtime)
        bets = self._update(bets, self._format_first_frag)
        bets = self._update(bets, self._format_win_at_least_number_of_maps)
        bets = self._update(bets, self._format_win_number_of_maps)
        bets = self._update(bets, self._format_individual_total_rounds)
        bets = self._update(bets, self._format_first_to_win_number_of_rounds)
        bets = self._update(bets, self._format_total_frags)

        bets = self._format_after(bets)

        bets = self._format_odds(bets)
        bets = self._format_bookmaker_name(bets)
        bets = self._format_titles(bets)

        return bets

    def _format_before(self, bets):
        """
        Apply unified syntax formatting to the given bets dict before obligatory updates are run. Subclass specific

        :param bets: bets dictionary to format
        :type bets: dict
        :return: formatted bets dictionary
        :rtype: dict
        """
        return bets

    def _format_after(self, bets):
        """
        Apply unified syntax formatting to the given bets dict after obligatory updates are run. Subclass specific

        :param bets: bets dictionary to format
        :type bets: dict
        :return: formatted bets dictionary
        :rtype: dict
        """
        return bets

    @abstractmethod
    def _get_name(self):
        pass

    def _get_invalid_bet_titles(self):
        return ()

    def _update(self, bets, _callable):
        """
        Update self.bets and given bets dictionaries according to _callable method

        :param bets: bets dictionary to format
        :type bets: dict
        :param _callable: method to be called to get formatted bet title
        :type _callable: method
        :return: updated bets dictionary
        :rtype: dict
        """
        invalid_bet_titles = self._get_invalid_bet_titles()

        for self.match_title in bets:
            for self.bet_title, odds in list(bets[self.match_title].items()):
                formatted_title = _callable()
                self.bets[self.match_title].pop(self.bet_title)

                if self.bet_title not in invalid_bet_titles:
                    self.bets[self.match_title][formatted_title] = odds

        return self.bets.copy()

    def _format_bookmaker_name(self, bets):
        """
        Add bookmakers name to the bets dict
        bets[match_title][bet_title] = odds -> bets[match_title][bet_title] = {odds: bookmaker}

        :param bets: bets dictionary to format
        :type bets: dict
        :return: updated bets dictionary
        :rtype: dict
        """
        name = self._get_name()

        for match_title in bets:
            url = self.bets[match_title][AbstractScraper.match_url_key]
            for bet_title, odds in bets[match_title].items():
                try:
                    self.bets[match_title][bet_title] = {odds: name + '(' + url + ')'}
                except KeyError:
                    self.bets[match_title][bet_title] = {odds: name}
            bets[match_title].pop(AbstractScraper.match_url_key)

        return self.bets.copy()

    def _format_titles(self, bets):
        """
        Remove specific words from titles

        :param bets: bets dictionary to format
        :type bets: dict
        :return: updated bets dictionary
        :rtype: dict
        """
        bets = self._format_match_titles(bets)
        bets = self._format_bet_titles(bets)

        return bets

    def _format_bet_titles(self, bets):
        """
        Remove specific words from bet titles

        :param bets: bets dictionary to format
        :type bets: dict
        :return: updated bets dictionary
        :rtype: dict
        """
        for match_title in bets:
            for bet_title in list(bets[match_title]):
                formatted_bet_title = bet_title
                for word in self._REMOVE_FROM_TITLES:
                    formatted_bet_title = formatted_bet_title.replace(word, '')

                self.bets[match_title][formatted_bet_title] = self.bets[match_title].pop(bet_title)

        return self.bets.copy()

    def _format_match_titles(self, bets):
        """
        Remove specific words from match titles

        :param bets: bets dictionary to format
        :type bets: dict
        :return: updated bets dictionary
        :rtype: dict
        """
        for match_title in bets:
            teams = MatchTitleCompiler.decompile_match_title(match_title)
            formatted_match_title = MatchTitleCompiler.compile_match_title(*teams, sort=True)
            swapped = formatted_match_title != match_title

            for word in self._REMOVE_FROM_TITLES:
                formatted_match_title = formatted_match_title.replace(word, '')

            if swapped:
                for bet_title in list(self.bets[match_title]):
                    if 'correct score ' in bet_title:
                        score1 = bet_title[len('correct score ')]
                        score2 = bet_title[len('correct score ') + 2]
                        formatted_bet_title = bet_title[:-3] + score2 + '-' + score1 + self._REMOVE_FROM_TITLES[0]
                        self.bets[match_title][formatted_bet_title] = self.bets[match_title].pop(bet_title)

            self.bets[formatted_match_title] = self.bets.pop(match_title)

        return self.bets.copy()

    def _format_odds(self, bets):
        """
        Remove empty odds bet titles

        :param bets: bets dictionary to format
        :type bets: dict
        :return: updated bets dictionary
        :rtype: dict
        """
        for match_title in bets:
            for bet_title, odds in list(bets[match_title].items()):
                if not odds:
                    self.bets[match_title].pop(bet_title)

        return self.bets.copy()

    def _format_team_names(self):
        formatted_title = self.bet_title.lower()
        for item in self._REMOVE_FROM_TITLES:
            formatted_title = formatted_title.replace(item, '', 1)
        return formatted_title

    def _format_win(self):
        return self.bet_title.lower()

    def _format_total(self):
        return self.bet_title.lower()

    def _format_maps(self):
        return self.bet_title.lower()

    def _format_handicap(self):
        return self.bet_title.lower()

    def _format_uncommon_chars(self):
        return self.bet_title.lower()

    def _format_win_in_round(self):
        return self.bet_title.lower()

    def _format_correct_score(self):
        return self.bet_title.lower()

    def _format_bomb_exploded(self):
        return self.bet_title.lower()

    def _format_bomb_planted(self):
        return self.bet_title.lower()

    def _format_overtime(self):
        return self.bet_title.lower()

    def _format_first_frag(self):
        return self.bet_title.lower()

    def _format_win_at_least_number_of_maps(self):
        return self.bet_title.lower()

    def _format_win_number_of_maps(self):
        return self.bet_title.lower()

    def _format_individual_total_rounds(self):
        return self.bet_title.lower()

    def _format_first_to_win_number_of_rounds(self):
        return self.bet_title.lower()

    def _format_total_frags(self):
        return self.bet_title.lower()
