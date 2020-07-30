from difflib import SequenceMatcher
from pprint import pformat
import re

from bet import Bet
from bet_group import BetGroup
from match_title import MatchTitle


class Match:
    def __init__(self, title: MatchTitle, url: str, date, bets=None):
        if bets is None:
            bets = []
        self.title = title
        self.url = url
        self.date = date
        self.bets = bets

    @classmethod
    def from_dict(cls, match_dict):
        date = None
        title = None
        key = list(match_dict.keys())[0]
        match = re.search(r'^((.+?): )?(.+?)$', key)
        if match:
            date = match.group(2)
            title = MatchTitle.from_str(match.group(3))

        bets_dict = list(match_dict.values())[0][0]
        bets = [Bet.from_dict({bet_title: odds}) for bet_title, odds in bets_dict.items()]

        return cls(title, '', date, bets)

    def to_dict(self):
        result = {}
        for bet in self.bets:
            value = None
            if type(bet) == Bet:
                value = str(bet.odds) + '(' + str(bet.bookmaker) + ' - ' + str(bet.url) + ')'
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
        return pformat({date_str + str(self.title): self.to_dict()}, width=300)
