

class ParimatchSyntaxFormatter:
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the websites
    """

    @staticmethod
    def format_team_name(team_name):
        """
        Removes extra spaces from the team name and converts letters to
        lowercase

        :param team_name: name of the team
        :type team_name: str
        :return: formatted team name
        :rtype: str
        """
        if team_name[0] == ' ':
            team_name = team_name[1:]
        if team_name[-1] == ' ':
            team_name = team_name[:-1]
        return str(team_name).lower()
