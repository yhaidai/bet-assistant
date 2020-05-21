import re


class SyntaxFormatter:
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the websites
    """

    # sport_names = {
    #     'counter-strike': 'csgo',
    #     'csgo': 'csgo',
    #     'CS:GO': 'csgo',
    # }
    #
    # bet_names = {
    #
    # }

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
    def compile_match_title(first_team, second_team, separator=' - '):
        """
        Compiles match title from two teams names

        :param first_team: name of the first team
        :type first_team: str
        :param second_team: name of the second team
        :type second_team: str
        :param separator: separator to be placed between the team names
        :type separator: str
        :return: match title, which consists of first and second team names
        in lowercase divided by separator string OR just a first team's name in
        case of second_team being equal to None
        :rtype: str
        """
        match_title = SyntaxFormatter.format_team_name(first_team)
        if second_team:
            match_title += separator + SyntaxFormatter.format_team_name(second_team)

        return match_title

    @staticmethod
    def decompile_match_title(match_title, separator=' - '):
        """
        Compiles match title from two teams names

        :param match_title: match title, which consists of first and
        second team names in lowercase divided by separator string
        :type match_title: str
        :param separator: separator placed between the team names
        :type separator: str
        :return: list which consists of first team name and second team name
        :rtype: list<str>
        """
        return re.split(separator, match_title)

    # @staticmethod
    # def get_sport_type(url):
    #     for name in SyntaxFormatter.sport_names.keys():
    #         if name in url:
    #             return SyntaxFormatter.sport_names[name]
    #
    #     return None
