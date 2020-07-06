class Bet:
    def __init__(self, title: str, odds: str):
        self.title = title
        self.odds = odds

    @classmethod
    def from_dict(cls, bets_dict):
        return cls(list(bets_dict.keys())[0], list(bets_dict.values())[0])

    def __repr__(self):
        return self.title + ': ' + self.odds
