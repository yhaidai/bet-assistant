import re
from pprint import pprint

from syntax_formatters.sample_data.one_x_bet import bets as b


class Grouper:
    @staticmethod
    def group(bets):
        result = {}
        grouped_by = {
            '(^\d-.{2} map: )?.+? will (win)$': (2, ),
            '(^\d-.{2} map: )?.+? will (win in round \d+)$': (2, ),
            '(correct score) \d+-\d+$': (1, ),
            '(^\d-.{2} map: )?(total) (over|under) (\d+(\.\d)?)$': (2, 4),
            '(^\d-.{2} map: )?(total) — (even|odd)$': (2, ),
            }
        for match_title in bets:
            result[match_title] = {}
            groups = {}
            for bet_title, odds in bets[match_title].items():
                for regex, match_group_numbers in grouped_by.items():
                    match = re.search(regex, bet_title)
                    if match:
                        key = ''
                        if match.group(1):
                            key = match.group(1)
                        for match_group_number in match_group_numbers:
                            key += match.group(match_group_number) + ' '
                        key = key[:-1]

                        groups.setdefault(key, {}).update({bet_title: odds})
                        continue

                match = re.search('(^\d-.{2} map: )?(^.+? )?(handicap )(.+? )?(\+|-)(\d+(\.\d)?)$', bet_title)
                if match:
                    key = None
                    for group in groups:
                        if not match.group(1):
                            if match.group(6) in group and match.group(3) in group \
                                    and match.group(2) not in group and match.group(5) not in group:
                                key = group
                        else:
                            if match.group(6) in group and match.group(3) in group and match.group(4) not in group \
                                    and match.group(5) not in group[len(match.group(1)):]:
                                key = group

                    if not key:
                        try:
                            key = match.group(1) + match.group(3) + match.group(4) + match.group(5) + match.group(6)
                        except TypeError:
                            key = match.group(2) + match.group(3) + match.group(5) + match.group(6)
                    groups.setdefault(key, {}).update({bet_title: odds})
                    continue

            result[match_title] = groups

        return result


if __name__ == '__main__':
    fork_bets = Grouper.group(b)
    pprint(fork_bets)
