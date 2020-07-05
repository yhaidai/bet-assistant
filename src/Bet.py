class Bet:
    def __init__(self, title: str, odds: str):
        self.title = title
        self.odds = odds

    def __repr__(self):
        return self.title + ': ' + self.odds
