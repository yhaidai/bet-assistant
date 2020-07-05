class BetGroup:
    def __init__(self, title: str, bets=None):
        if bets is None:
            bets = []
        self.title = title
        self.bets = bets
