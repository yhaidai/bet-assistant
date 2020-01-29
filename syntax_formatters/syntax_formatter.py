

class SyntaxFormatter:
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

    @staticmethod
    def compile_match_title(first_team, second_team):
        """
        Compiles match title from two teams names

        :param first_team: name of the first team
        :type first_team: str
        :param second_team: name of the second team
        :type second_team: str
        :return: match title, which consists of first and second team names
        in lowercase divided by ' - ' string OR just a first team's name in
        case of second_team being equal to None
        """
        match_title = SyntaxFormatter.format_team_name(first_team)
        print(second_team)
        if second_team:
            match_title += ' - ' + SyntaxFormatter.format_team_name(
                second_team)

        return match_title
