import re
from pprint import pformat


class Bet:
    def __init__(self, title: str, odds: str, bookmaker: str, url: str):
        self.title = title
        self.odds = odds
        self.bookmaker = bookmaker
        self.url = url

    @classmethod
    def from_dict(cls, bet_dict):
        title = list(bet_dict.keys())[0]
        odds = None
        bookmaker = None
        url = None
        value = list(bet_dict.values())[0]
        match = re.search(r'^(.+?)\((.+?) - (.+?)\)$', value)
        if match:
            odds = match.group(1)
            bookmaker = match.group(2)
            url = match.group(3)

        return cls(title, odds, bookmaker, url)

    def __repr__(self):
        key = str(self.title)
        value = str(self.odds) + '(' + str(self.bookmaker) + ' - ' + str(self.url) + ')'
        return pformat({key: value}, width=300)

    def __gt__(self, other):
        return float(self.odds) > float(other.odds)
