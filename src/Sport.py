from pprint import pformat, pprint

from Match import Match
from scrapers.sample_data.csgo import parimatch


class Sport:
    def __init__(self, name: str, matches: list):
        self.name = name
        self.matches = matches

    @classmethod
    def from_dict(cls, sport_dict):
        matches_dict = list(sport_dict.values())[0]
        matches = [Match.from_dict({match_title: bets}) for match_title, bets in matches_dict.items()]

        return cls(list(sport_dict.keys())[0], matches)

    def to_dict(self):
        result = {}
        for match in self.matches:
            date_str = ''
            if match.date:
                date_str = match.date + ': '
            key = date_str + match.title + '(' + match.bookmaker + ' - ' + match.url + ')'
            result[key] = match.to_dict()
        return result

    def __iter__(self):
        return iter(self.matches)

    def __next__(self):
        return next(self.matches)

    def __repr__(self):
        return pformat({self.name: self.to_dict()})


if __name__ == '__main__':
    sport = Sport.from_dict(parimatch.bets)
    pprint(sport)
