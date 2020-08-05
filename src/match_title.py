class MatchTitle:
    def __init__(self, teams: list):
        self.teams = [team.lower() for team in teams]

    @classmethod
    def from_str(cls, text: str):
        teams = text.split(' - ')
        return cls(teams)

    def __repr__(self):
        return ' - '.join(self.teams)

    def __eq__(self, other):
        return self.teams == other.teams

    def __hash__(self):
        return hash(tuple(self.teams))


if __name__ == '__main__':
    mt = MatchTitle(['ast', 'g2', 'cloud9'])
    print(mt)
    mt = MatchTitle.from_str('astralis - g2 - cloud9')
    print(mt.teams)
