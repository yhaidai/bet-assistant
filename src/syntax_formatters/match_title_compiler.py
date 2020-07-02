import re


class MatchTitleCompiler:
    """
    Class for compiling/decompiling match titles
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
    def compile_match_title(first_team, second_team, sort=False, separator=' - '):
        """
        Compiles match title from two team names

        :param first_team: name of the first team
        :type first_team: str
        :param second_team: name of the second team
        :type second_team: str
        :param sort: whether to sort team names or not
        :type sort: bool
        :param separator: separator to be placed between the team names
        :type separator: str
        :return: match title, which consists of first and second team names
        in lowercase divided by separator string OR just a first team's name in
        case of second_team being equal to None
        :rtype: str
        """
        if sort:
            teams = [first_team, second_team]
            teams.sort()
            first_team = teams[0]
            if second_team:
                second_team = teams[1]

        match_title = MatchTitleCompiler.format_team_name(first_team)
        if second_team:
            match_title += separator + MatchTitleCompiler.format_team_name(second_team)

        return match_title

    @staticmethod
    def decompile_match_title(match_title, separator=' - '):
        """
        Decompiles match title into two team names

        :param match_title: match title, which consists of first and
        second team names in lowercase divided by separator string
        :type match_title: str
        :param separator: separator placed between the team names
        :type separator: str
        :return: list which consists of first team name and second team name
        :rtype: list<str>
        """
        return re.split(separator, match_title)
