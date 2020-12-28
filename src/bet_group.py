from pprint import pformat

from bet import Bet


class BetGroup:
    def __init__(self, title: str, bets=None, profit=None):
        if bets is None:
            bets = []
        self.title = title
        self.bets = bets
        self.profit = profit

    def __repr__(self):
        return pformat({bet.title: bet.odds for bet in self.bets})

    def __len__(self):
        return len(self.bets)

    def __iter__(self):
        return iter(self.bets)

    def __next__(self):
        return next(self.bets)

    def __getitem__(self, item: int):
        return self.bets[item]

    def to_dict(self):
        result = {}
        for bet in self.bets:
            result.setdefault(bet.title, []).append(bet)

        return result

    def append(self, bet: Bet):
        self.bets.append(bet)

    def get_odds(self):
        odds = []
        for bet in self.bets:
            odds.append(bet.odds)

        return odds
