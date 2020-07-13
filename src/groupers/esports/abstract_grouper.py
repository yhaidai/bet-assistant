import re
from abc import ABC, abstractmethod

from BetGroup import BetGroup
from Sport import Sport
from groupers.abstract_grouper import AbstractGrouper as AG


class AbstractGrouper(AG, ABC):
    _grouped_by = {
        r'(^\d-.{2} map: )?.+? will (win)$': (2, ),
        r'^(correct score) \d+-\d+$': (1, ),
        r'(^\d-.{2} map: )?(total) (over|under) (\d+(\.\d)?)$': (2, 4),
        r'(^\d-.{2} map: )?(total) — (even|odd)$': (2, ),
        }

    def group_bets(self, sport: Sport):
        self._get_grouped_by().update(AbstractGrouper._grouped_by)

        for match in sport:
            groups = {}
            for bet in match:
                for regex, match_group_numbers in self._grouped_by.items():
                    found = re.search(regex, bet.title)
                    if found:
                        key = ''
                        if found.group(1):
                            key = found.group(1)
                        if 1 not in match_group_numbers:
                            for match_group_number in match_group_numbers:
                                key += found.group(match_group_number) + ' '
                            key = key[:-1]

                        groups.setdefault(key, BetGroup(key)).append(bet)
                        continue

                found = re.search(r'(^\d-.{2} map: )(handicap )(.+? )(\+|-)(\d+(\.\d)?)$|'
                                  r'^(.+? )(handicap )(\+|-)(\d+(\.\d)? maps)$', bet.title)
                if found:
                    key = None
                    for group in groups:
                        if not found.group(1):
                            if found.group(10) in group and found.group(8) in group \
                                    and found.group(7) not in group and found.group(9) not in group:
                                key = group
                        else:
                            if found.group(5) in group and found.group(2) in group and found.group(1) in group and \
                                    found.group(3) not in group and found.group(4) not in group[len(found.group(1)):]:
                                key = group

                    if not key:
                        try:
                            key = found.group(1) + found.group(2) + found.group(3) + found.group(4) + found.group(5)
                        except TypeError:
                            key = found.group(7) + found.group(8) + found.group(9) + found.group(10)
                    groups.setdefault(key, BetGroup(key)).append(bet)
                    continue
            match.bets = list(groups.values())

        return sport

    @abstractmethod
    def _get_grouped_by(self):
        return self._get_grouped_by()
