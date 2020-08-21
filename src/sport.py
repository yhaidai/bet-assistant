import pickle
from pprint import pformat

from match import Match
from scrapers.sample_data.dota import one_x_bet


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
            date_time_str = ''
            url_str = ''
            if match.date_time:
                date_time_str = str(match.date_time) + ': '
            if match.url:
                url_str = match.url + ' '
            key = url_str + date_time_str + str(match.title)
            result.setdefault(key, []).append(match.to_dict())
        return result

    def __iter__(self):
        return iter(self.matches)

    def __next__(self):
        return next(self.matches)

    def __repr__(self):
        return pformat({self.name: self.to_dict()}, width=300)

    def __eq__(self, other):
        return self.name == other.name and self.matches == other.matches

    def __len__(self):
        return len(self.matches)

    def __getitem__(self, item: int):
        return self.matches[item]

    def serialize(self, filename):
        return pickle.dump(self, open(filename, 'wb'))

    @classmethod
    def deserialize(cls, filename):
        return pickle.load(open(filename, 'rb'))


if __name__ == '__main__':
    sport = Sport.from_dict(one_x_bet.sport)
    print(sport)
    filename = 'one_x_bet'
    sport.serialize(filename)
    sport2 = sport.deserialize(filename)
    print(sport == sport2)
