from pprint import pformat, pprint
import re

from Bet import Bet
from BetGroup import BetGroup


class Match:
    def __init__(self, title: str, bets: list, date=None):
        self.title = title
        self.bets = bets
        self.date = date

    @classmethod
    def from_dict(cls, match_dict):
        date = None
        title = None
        key = list(match_dict.keys())[0]
        match = re.search(r'^((.+?): )?(.+?)$', key)
        if match:
            date = match.group(2)
            title = match.group(3)

        bets_dict = list(match_dict.values())[0]
        bets = [Bet.from_dict({bet_title: odds}) for bet_title, odds in bets_dict.items()]

        return cls(title, bets, date)

    def to_dict(self):
        result = {}
        for bet in self.bets:
            value = None
            if type(bet) == Bet:
                value = bet
            elif type(bet) == BetGroup:
                value = bet.to_dict()

            result.setdefault(bet.title, []).append(value)

        return result

    def __iter__(self):
        return iter(self.bets)

    def __next__(self):
        return next(self.bets)

    def __repr__(self):
        date_str = ''
        if self.date:
            date_str = self.date + ': '
        return pformat({date_str + self.title: self.to_dict()}, width=300)
