

class ParimatchSyntaxFormatter:

    @staticmethod
    def format_team_name(team_name):
        """Removes extra spaces from the team name
        and converts letters to lowercase"""
        if team_name[0] == ' ':
            team_name = team_name[1:]
        if team_name[-1] == ' ':
            team_name = team_name[:-1]
        return str(team_name).lower()
