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
        url = None
        date_time = None
        title = None
        key = list(match_dict.keys())[0]
        found = re.search(r'^(https://.+?) (.+?): (.+?)$', key)
        if found:
            url = found.group(1)
            date_time = DateTime.fromisoformat(found.group(2))
            title = MatchTitle.from_str(found.group(3))

        bets_dict = list(match_dict.values())[0][0]
        bets = [Bet.from_dict({bet_title: odds}) for bet_title, odds in bets_dict.items()]

        return cls(title, url, date_time, None, bets)

    def to_dict(self):
        result = {}
        for bet in self.bets:
            value = None
            key = None
            if type(bet) == Bet:
                key = bet.title
                value = f'{bet.odds}: {bet.amount}({bet.bookmaker} - {bet.url})'
            elif type(bet) == BetGroup:
                key = f'Profit {bet.profit} - {bet.title}'
                value = bet.to_dict()

            result.setdefault(key, []).append(value)

        return result

    def __iter__(self):
        return iter(self.bets)

    def __next__(self):
        return next(self.bets)

    def __len__(self):
        return len(self.bets)

    def __eq__(self, other):
        return (self.url == other.url and self.title == other.title and
                self.date_time == other.date_time and self.scraper == other.scraper)

    def __hash__(self):
        return hash(self.url + str(self.date_time) + str(self.title) + self.scraper.get_name())

    def __getitem__(self, item: int):
        return self.bets[item]

    def __repr__(self):
        date_time_str = ''
        url_str = ''
        if self.date_time:
            date_time_str = str(self.date_time) + ': '
        if self.url:
            url_str = self.url + ' '
        return pformat({url_str + date_time_str + str(self.title): self.to_dict()}, width=300)
