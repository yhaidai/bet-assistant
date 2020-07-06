from pprint import pformat, pprint
import re

from Bet import Bet


class Match:
    def __init__(self, title: str, url: str, bookmaker: str, bets: list, date=None):
        self.title = title
        self.url = url
        self.bookmaker = bookmaker
        self.bets = bets
        self.date = date

    @classmethod
    def from_dict(cls, match_dict):
        date = None
        title = None
        bookmaker = None
        url = None
        key = list(match_dict.keys())[0]
        match = re.search(r'^((.+?): )?(.+?)\((.+?) - (.+?)\)$', key)
        if match:
            date = match.group(2)
            title = match.group(3)
            bookmaker = match.group(4)
            url = match.group(5)

        bets_dict = list(match_dict.values())[0]
        bets = [Bet.from_dict({bet_title: odds}) for bet_title, odds in bets_dict.items()]

        return cls(title, url, bookmaker, bets, date)

    def to_dict(self):
        result = {}
        for bet in self.bets:
            result[bet.title] = bet.odds
        return result

    def __iter__(self):
        return iter(self.bets)

    def __next__(self):
        return next(self.bets)

    def __repr__(self):
        date_str = ''
        if self.date:
            date_str = self.date + ': '
        return pformat({date_str + self.title + '(' + self.bookmaker + ' - ' + self.url + ')': self.to_dict()})
