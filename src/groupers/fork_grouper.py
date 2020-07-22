import re
from abc import ABC, abstractmethod

from bet_group import BetGroup
from match import Match
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
            first_match.title.teams.sort()
            groups.setdefault(first_match.title, set()).add(first_match)
            for second_match in sport_copy2:
                if first_match.similar(second_match, 0.8):
                    groups[first_match.title].add(second_match)
                    sport_copy1.remove(second_match)

                    if str(first_match.title) != str(second_match.title):
                        print(first_match.title)
                        print(second_match.title)
                        print()

                    second_match.title = first_match.title

            sport_copy2.remove(first_match)

        # for title, group in groups.items():
        #     all_bets = []
        #     for match in group:
        #         all_bets += match.bets
        #         print("Removing " + str(match.title))
        #         sport.matches.remove(match)
        #     all_bets_match = Match(title, '', '', all_bets)
        #     sport.matches.append(all_bets_match)

        return groups

    def group_bets(self, sport: Sport) -> Sport:
        grouped_by = self._get_grouped_by()

        for self.match in sport:
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

                if self.unhandled:
                    print(self.bet.bookmaker + ': ' + self.bet.title)

            self.match.bets = list(self.groups.values())

        return sport

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
