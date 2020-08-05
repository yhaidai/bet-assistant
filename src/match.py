from difflib import SequenceMatcher
from pprint import pformat
import re

from abstract_scraper import AbstractScraper
from bet import Bet
from bet_group import BetGroup
from date_time import DateTime
from match_title import MatchTitle


class Match:
    def __init__(self, title: MatchTitle, url: str, date_time: DateTime, scraper: AbstractScraper, bets=None):
        if bets is None:
            bets = []
        self.title = title
        self.url = url
        self.date_time = date_time
        self.scraper = scraper
        self.bets = bets

    @classmethod
    def from_dict(cls, match_dict):
        date_time = None
        title = None
        key = list(match_dict.keys())[0]
        found = re.search(r'^((.+?): )?(.+?)$', key)
        if found:
            date_time = DateTime.fromisoformat(found.group(2))
            title = MatchTitle.from_str(found.group(3))

        bets_dict = list(match_dict.values())[0][0]
        bets = [Bet.from_dict({bet_title: odds}) for bet_title, odds in bets_dict.items()]

        return cls(title, '', date_time, None, bets)

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

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)

    def __repr__(self):
        date_str = ''
        if self.date_time:
            date_str = str(self.date_time) + ': '
        return pformat({self.url + ' ' + date_str + str(self.title): self.to_dict()}, width=300)

    # def __repr__(self):
    #     return 'Match(id=' + str(id(self)) + ')'
