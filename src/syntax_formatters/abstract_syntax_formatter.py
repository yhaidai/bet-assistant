from abc import ABC, abstractmethod


class AbstractSyntaxFormatter(ABC):
    invalid_bet_titles = []
    remove_from_titles = ['team ', ' esports', ' club']

    def __init__(self, bets):
        self.bets = bets.copy()
        self.apply_unified_syntax_formatting(bets)

    def apply_unified_syntax_formatting(self, bets):
        bets = self._apply_unified_syntax_formatting(bets)
        bets = self._format_odds(bets)
        bets = self._format_bookmaker_name(bets)
        bets = self._format_titles(bets)

    @abstractmethod
    def _apply_unified_syntax_formatting(self, bets):
        pass

    def _update(self, bets, _callable):
        for self.match_title in bets:
            for self.bet_title, odds in list(bets[self.match_title].items()):
                formatted_title = _callable()
                self.bets[self.match_title].pop(self.bet_title)
                if self.bet_title not in self.invalid_bet_titles:
                    self.bets[self.match_title][formatted_title] = odds

        return self.bets.copy()

    def _format_bookmaker_name(self, bets):
        for match_title in bets:
            for bet_title, odds in bets[match_title].items():
                self.bets[match_title][bet_title] = {odds: self.name}

        return self.bets.copy()

    def _format_titles(self, bets):
        bets = self._format_bet_titles(bets)
        bets = self._format_match_titles(bets)

        return bets

    def _format_bet_titles(self, bets):
        for match_title in bets:
            for bet_title in bets[match_title].keys():
                # print(bet_title)
                formatted_bet_title = bet_title
                for word in self.remove_from_titles:
                    formatted_bet_title = formatted_bet_title.replace(word, '')

                self.bets[match_title][formatted_bet_title] = self.bets[match_title].pop(bet_title)
                if bet_title == '1-st map: chiefs esports club will win in round 1':
                    print(formatted_bet_title)

        return self.bets.copy()

    def _format_match_titles(self, bets):
        for match_title in bets:
            formatted_match_title = match_title
            for word in self.remove_from_titles:
                formatted_match_title = formatted_match_title.replace(word, '')

            self.bets[formatted_match_title] = self.bets.pop(match_title)

        return self.bets.copy()

    def _format_odds(self, bets):
        for match_title in bets:
            for bet_title, odds in list(bets[match_title].items()):
                if not odds:
                    self.bets[match_title].pop(bet_title)

        return self.bets.copy()
