class MatchTitle:
    def __init__(self, teams: list):
        self.teams = [team.lower() for team in teams]

    @classmethod
    def from_str(cls, text: str):
        teams = text.split(' - ')
        return cls(teams)

    def __repr__(self):
        return ' - '.join(self.teams)

    def __contains__(self, item):
        return item in self.teams

    def replace(self, team, replacement):
        index = self.teams.index(team)
        self.teams.remove(team)
        self.teams.insert(index, replacement)

    def get_teams(self):
        try:
            return self.raw_teams
        except AttributeError:
            return self.teams


if __name__ == '__main__':
    mt = MatchTitle(['ast', 'g2', 'cloud9'])
    print(mt)
    mt = MatchTitle.from_str('astralis - g2 - cloud9')
    print(mt.teams)
