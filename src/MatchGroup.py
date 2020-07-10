from pprint import pformat

from Bet import Bet
from Match import Match


class MatchGroup:
    def __init__(self, title: str, matches=None):
        if matches is None:
            matches = []
        self.title = title
        self.matches = matches

    def __repr__(self):
        matches_dict = {}
        for match in self.matches:
            matches_dict.setdefault(match.title, []).append(match.bets)

        return pformat(matches_dict)

    def __iter__(self):
        return iter(self.matches)

    def __next__(self):
        return next(self.matches)

    def append(self, match: Match):
        self.matches.append(match)
