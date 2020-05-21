from abc import ABC, abstractmethod


class AbstractSyntaxFormatter(ABC):
    def __init__(self, bets):
        self.bets = bets.copy()
        self.apply_unified_syntax_formatting(bets)

    @abstractmethod
    def apply_unified_syntax_formatting(self, bets):
        pass

    def _update(self, bets, _callable):
        for self.match_title in bets.keys():
            for self.bet_title, odds in list(bets[self.match_title].items()):
                formatted_title = _callable()
                self.bets[self.match_title].pop(self.bet_title)
                self.bets[self.match_title][formatted_title] = odds

        return self.bets.copy()
