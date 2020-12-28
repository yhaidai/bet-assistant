import xlsxwriter
import pickle
from pprint import pformat

from bet_group import BetGroup
from constants import SPORT_NAME
from match import Match


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

    def write_xlsx(self, filename):
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        row = 0
        column = 0

        column_names = ['Match', 'Time', 'Profit', 'Bet', 'Odds', 'Bet amount', 'Bookmaker', 'URL']
        for column_name in column_names:
            worksheet.write(row, column, column_name)
            column += 1
        row += 1

        for match in self:
            match_title = match.title
            match_date_time = match.date_time
            for bet_group in match:
                profit = bet_group.profit
                if isinstance(bet_group, BetGroup):
                    for bet in bet_group:
                        values = [str(match_title), str(match_date_time), str(profit), bet.title, bet.odds,
                                  str(bet.amount), bet.bookmaker, bet.url]
                        column = 0
                        for value in values:
                            worksheet.write(row, column, value)
                            column += 1

                        row += 1
                        match_title = ''
                        match_date_time = ''
                        profit = ''

        workbook.close()


if __name__ == '__main__':
    sport = Sport.deserialize(f'arbitrager\\sample_data\\{SPORT_NAME}')
    print(sport)
    sport.write_xlsx(f'{SPORT_NAME}.xlsx')
