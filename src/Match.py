from pprint import pformat


class Match:
    def __init__(self, title: str, url: str, bookmaker: str, bets: list, date=None):
        self.title = title
        self.url = url
        self.bookmaker = bookmaker
        self.bets = bets
        self.date = date

    def bets_dict(self):
        result = {}
        for bet in self.bets:
            result[bet.title] = bet.odds
        return result

    def __repr__(self):
        date_str = ''
        if self.date:
            date_str = self.date + ': '
        return pformat({date_str + self.title + '(' + self.bookmaker + ' - ' + self.url + ')': self.bets_dict()})
