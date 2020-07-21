class MatchTitle:
    def __init__(self, teams: list):
        self.teams = [team.lower() for team in teams]

    def __repr__(self):
        return ' - '.join(self.teams)

    @classmethod
    def from_str(cls, text: str):
        teams = text.split(' - ')
        return cls(teams)


if __name__ == '__main__':
    mt = MatchTitle(['ast', 'g2', 'cloud9'])
    print(mt)
    mt = MatchTitle.from_str('astralis - g2 - cloud9')
    print(mt.teams)
