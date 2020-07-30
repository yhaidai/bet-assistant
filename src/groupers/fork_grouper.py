import re
from abc import ABC, abstractmethod
from pprint import pprint

from bet_group import BetGroup
from match import Match
from match_comparator import MatchComparator
from sport import Sport


class ForkGrouper(ABC):
    _grouped_by = {
        r'^(correct score) \d+-\d+$': (1,),
    }

    def __init__(self):
        self.groups = {}
        self.match = None
        self.bet = None

    @staticmethod
    def get_match_groups(sport: Sport) -> dict:
        groups = {}

        sport_copy1 = list(sport)
        sport_copy2 = list(sport)
        for first_match in sport_copy1:
            if first_match.title in groups:
                continue
            sport_copy2.remove(first_match)
            first_match.title.raw_teams = list(first_match.title.teams)
            first_match.title.teams.sort()
            groups.setdefault(first_match.title, []).append(first_match)
            for second_match in sport_copy2:
                if second_match.scraper == first_match.scraper:
                    continue
                comparator = MatchComparator()
                if comparator.similar(first_match, second_match, 0.8):
                    groups[first_match.title].append(second_match)

                    # if str(first_match.title) != str(second_match.title):
                    #     print(first_match.title)
                    #     print(second_match.title)
                    #     print()
                    first_match.title.similarities = comparator.similarities
                    second_match.title.similarities = comparator.similarities

                    second_match.title.raw_teams = second_match.title.teams
                    second_match.title.teams = first_match.title.teams
                    # TODO: replace break with max similarity search
                    break

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

        # print('Groups:')
        # pprint(self.groups)
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
