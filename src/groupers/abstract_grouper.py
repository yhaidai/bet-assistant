from abc import ABC, abstractmethod

from Match import Match
from Sport import Sport


class AbstractGrouper(ABC):
    @staticmethod
    def group_matches(sport: Sport):
        groups = {}

        for match in sport:
            groups.setdefault(match.title, []).append(match)

        for title, group in groups.items():
            all_bets = []
            for match in group:
                all_bets += match.bets
                sport.matches.remove(match)
            all_bets_match = Match(title, all_bets)
            sport.matches.append(all_bets_match)

        return sport

    @abstractmethod
    def group_bets(self, sport: Sport):
        pass
