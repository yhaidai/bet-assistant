import re
from abc import ABC, abstractmethod
from pprint import pprint

from bet_group import BetGroup
from match import Match
from match_comparator import MatchComparator
from match_title import MatchTitle
from sport import Sport


class ForkGrouper(ABC):
    _grouped_by = {
        r'^(correct score) \d+-\d+$': (1,),
        }

    def __init__(self):
        self._certainty = 0.5
        self.groups = {}
        self.match = None
        self.bet = None

    @staticmethod
    def _match_in_groups(match: Match, title: MatchTitle, groups: dict) -> bool:
        try:
            group = groups[title]
            return match in group
        except KeyError:
            return False

    @staticmethod
    def _match_in_groups_by_title_teams_and_date_time(match: Match, groups: dict) -> bool:
        for title_, group in groups.items():
            if match.title.teams == title_.teams and match.date_time == group[0].date_time:
                return match in group

        return False

    def _handle_same_scrapers_in_group(self, match: Match, group: list):
        comparator = MatchComparator()
        for match_ in group[:]:
            if match_.scraper == match.scraper and match != match_:
                teams_ = match.title.teams
                match_.title.teams = match_.title.raw_teams

                similarity = comparator.calculate_matches_similarity(group[0], match, self._certainty)
                similarity_ = comparator.calculate_matches_similarity(group[0], match_, self._certainty)
                # print(group[0])
                # print(similarity, match)
                # print(similarity_, match_)
                if similarity > similarity_:
                    group.remove(match_)
                    match_.title.teams = teams_
                else:
                    group.remove(match)

    def get_match_groups(self, sport: Sport) -> dict:
        groups = {}

        sport_copy1 = list(sport)
        sport_copy2 = list(sport)
        for first_match in sport_copy1:
            sport_copy2.remove(first_match)
            if ForkGrouper._match_in_groups_by_title_teams_and_date_time(first_match, groups):
                continue
            first_match.title.raw_teams = list(first_match.title.teams)
            first_match.title.teams.sort()
            groups.setdefault(first_match.title, []).append(first_match)

            similarities = {}
            group = groups[first_match.title]
            for second_match in sport_copy2:
                comparator = MatchComparator()
                if ForkGrouper._match_in_groups_by_title_teams_and_date_time(second_match, groups):
                    continue
                if comparator.similar(first_match, second_match, self._certainty):

                    group.append(second_match)
                    self._handle_same_scrapers_in_group(second_match, group)

                    if ForkGrouper._match_in_groups(second_match, first_match.title, groups):
                        # print(first_match)
                        # print(second_match)
                        # print()

                        for key, value in comparator.similarities.items():
                            if key in similarities:
                                if len(value) == len(similarities[key]):
                                    min_team = min(value, similarities[key])
                                elif len(value) > len(similarities[key]):
                                    min_team = similarities[key]
                                else:
                                    min_team = value

                                similarities[key] = min_team
                            else:
                                similarities[key] = value

                        first_match.title.similarities = comparator.similarities
                        second_match.title.similarities = comparator.similarities
                        second_match.title.raw_teams = second_match.title.teams
                        second_match.title.teams = first_match.title.teams

            for match in group:
                for team in match.title.teams:
                    if team in similarities:
                        match.title.replace(team, similarities[team])

        return groups

    def group_bets(self, match: Match) -> None:
        self.match = match
        grouped_by = self._get_grouped_by()

        self.groups = {}
        for self.bet in self.match:
            self.unhandled = True

            for pattern, match_group_numbers in grouped_by.items():
                found = re.search(pattern, self.bet.title)
                if found:
                    self.unhandled = False
                    key = ''
                    if found.group(1):
                        key = found.group(1)
                    if 1 not in match_group_numbers:
                        for match_group_number in match_group_numbers:
                            key += found.group(match_group_number) + ' '
                        key = key[:-1]

                    self.groups.setdefault(key, BetGroup(key)).append(self.bet)

            self._group_handicaps()

            # if self.unhandled:
            #     print(self.bet.bookmaker + ': ' + self.bet.title)

        self.match.bets = list(self.groups.values())

    @abstractmethod
    def _get_handicap_targets(self):
        pass

    @abstractmethod
    def _get_handicap_pattern_prefix(self) -> str:
        pass

    def _compile_handicap_pattern(self) -> str:
        result = self._get_handicap_pattern_prefix()
        handicap_targets = self._get_handicap_targets()
        result += '|'.join(handicap_targets) + '))$'
        return result

    def _group_handicaps(self) -> None:
        sign_opposites = {
            '+': '-',
            '-': '+',
            '': '',
            }
        handicap_pattern = self._compile_handicap_pattern()

        found = re.search(handicap_pattern, self.bet.title)
        if found:
            self.unhandled = False
            key = found.group(1)
            teams = self.match.title.teams
            if found.group('team_name') == teams[1]:
                key = key.replace(found.group('team_name'), teams[0])
                sign = found.group('sign')
                prefix_length = len(str(found.group('prefix')))
                key = key[:prefix_length] + key[prefix_length:].replace(sign, sign_opposites[sign])

            self.groups.setdefault(key, BetGroup(key)).append(self.bet)

    def _get_grouped_by(self) -> dict:
        return ForkGrouper._grouped_by
