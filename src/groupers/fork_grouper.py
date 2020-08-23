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

    def get_match_groups(self, sport: Sport) -> dict:
        # TODO: modify algorithm to handle cases with match being absent on one of the
        #  websites(other similar match may be taken into group in such case)
        groups = {}

        sport_copy1 = list(sport)
        sport_copy2 = list(sport)
        for first_match in sport_copy1:
            sport_copy2.remove(first_match)
            if hasattr(first_match.title, 'raw_teams'):
                continue

            first_match.title.raw_teams = list(first_match.title.teams)
            first_match.title.teams.sort()
            groups.setdefault(first_match.title, []).append(first_match)
            group = groups[first_match.title]
            similarities = {}
            for second_match in sport_copy2:
                comparator = MatchComparator()
                if hasattr(second_match.title, 'raw_teams'):
                    continue

                if comparator.similar(first_match, second_match, self._certainty):
                    group.append(second_match)
                    self._handle_same_scrapers_in_group(second_match, group, similarities)

                    if second_match in group:
                        # key is the team that needs to be changed, value is the team that key needs to be changed into
                        for key, value in comparator.similarities.items():
                            similarities.setdefault(key, []).append({second_match: value})

                        first_match.title.similarities = comparator.similarities
                        second_match.title.similarities = comparator.similarities
                        second_match.title.raw_teams = second_match.title.teams
                        second_match.title.teams = first_match.title.teams

            if len(group) < 2:
                first_match.title.teams = first_match.title.raw_teams
                delattr(first_match.title, 'raw_teams')
                continue

            similarities_clean = first_match.title.similarities
            for key, match_value_pairs in similarities.items():
                min_team = self._find_min_team_for_key(key, match_value_pairs, group, similarities_clean)
                # every other similar team will then need to be changed into min team
                self._update_similarities(key, min_team, similarities_clean, match_value_pairs)

            self._minimize_titles(group, similarities_clean)
            # TODO: run one more search for similar matches for min title

        return groups

    def _handle_same_scrapers_in_group(self, match: Match, group: list, similarities: dict) -> None:
        comparator = MatchComparator()
        for match_ in group[:]:
            if match_.scraper == match.scraper and match != match_:
                teams_ = match_.title.teams
                match_.title.teams = match_.title.raw_teams

                similarity = comparator.calculate_matches_similarity(group[0], match, self._certainty)
                similarity_ = comparator.calculate_matches_similarity(group[0], match_, self._certainty)

                match_.title.teams = teams_

                if similarity > similarity_:
                    match_.title.teams = match_.title.raw_teams
                    delattr(match_.title, 'raw_teams')
                    delattr(match_.title, 'similarities')
                    group.remove(match_)
                else:
                    group.remove(match)

    @staticmethod
    def _find_min_team_for_key(key: str, match_value_pairs: list, group: dict, similarities_clean: dict) -> str:
        min_team = None
        for match_value_pair in match_value_pairs:
            for match, value in match_value_pair.items():
                if match in group:
                    if min_team is None:
                        min_team = value
                    else:
                        if key in similarities_clean:
                            if len(value) == len(min_team):
                                min_team = min(value, min_team)
                            elif len(value) < len(min_team):
                                min_team = value

        if min_team:
            # if min_team already has a shorter version - use it
            while min_team in similarities_clean and min_team != similarities_clean[min_team]:
                min_team = similarities_clean[min_team]

        return min_team

    @staticmethod
    def _update_similarities(key: str, min_team: str, similarities_clean: dict, match_value_pairs: list) -> None:
        if min_team:
            for k, v in list(similarities_clean.items()):
                # if current key is a value for some other other key - replace it there with min_team
                if v == key:
                    similarities_clean[k] = min_team
                # if current key already has some value - replace its value with min_team
                if k == key:
                    similarities_clean[v] = min_team

            # all teams in the group that belong to this key will then need to be changed into min team
            similarities_clean[key] = min_team
            for match_value_pair in match_value_pairs:
                for value in match_value_pair.values():
                    if value != min_team:
                        similarities_clean[value] = min_team

    @staticmethod
    def _minimize_titles(group: list, similarities: dict) -> None:
        for match in group:
            for team in match.title.teams:
                if team in similarities:
                    match.title.replace(team, similarities[team])

            match.title.similarities = similarities

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
