from difflib import SequenceMatcher
from pprint import pformat
import re

from bet import Bet
from bet_group import BetGroup
from match_title import MatchTitle


class Match:
    def __init__(self, title: MatchTitle, url: str, date, bets=None):
        if bets is None:
            bets = []
        self.title = title
        self.url = url
        self.date = date
        self.bets = bets

    @classmethod
    def from_dict(cls, match_dict):
        date = None
        title = None
        key = list(match_dict.keys())[0]
        match = re.search(r'^((.+?): )?(.+?)$', key)
        if match:
            date = match.group(2)
            title = MatchTitle.from_str(match.group(3))

        bets_dict = list(match_dict.values())[0]
        bets = [Bet.from_dict({bet_title: odds}) for bet_title, odds in bets_dict.items()]

        return cls(title, '', date, bets)

    def to_dict(self):
        result = {}
        for bet in self.bets:
            value = None
            if type(bet) == Bet:
                value = str(bet.odds) + '(' + str(bet.bookmaker) + ' - ' + str(bet.url) + ')'
            elif type(bet) == BetGroup:
                value = bet.to_dict()

            result.setdefault(bet.title, []).append(value)

        return result

    def __iter__(self):
        return iter(self.bets)

    def __next__(self):
        return next(self.bets)

    def __repr__(self):
        date_str = ''
        if self.date:
            date_str = self.date + ': '
        return pformat({date_str + str(self.title): self.to_dict()}, width=300)

    def similar(self, other, certainty):
        similarity = Match._calculate_matches_similarity(self, other)
        return similarity >= certainty

    @staticmethod
    def _calculate_matches_similarity(first_match, second_match):
        teams1 = first_match.title.teams
        teams2 = second_match.title.teams

        if len(teams1) != len(teams2):
            return 0

        total_similarity = 0
        teams2_copy = list(teams2)
        for first_team in teams1:
            max_similarity = -1
            max_similarity_second_team = None
            for second_team in teams2_copy:
                similarity = Match._calculate_teams_similarity(first_team, second_team)
                # print(similarity)
                if similarity > max_similarity:
                    max_similarity = similarity
                    max_similarity_second_team = second_team

            total_similarity += max_similarity

            # print(teams1)
            # print(teams2_copy)
            # print(max_similarity_second_team)
            # print()
            teams2_copy.remove(max_similarity_second_team)

        relative_total_similarity = total_similarity / len(teams1)
        return relative_total_similarity

    @staticmethod
    def _calculate_teams_similarity(first_team: str, second_team: str):
        min_initial_length = min(len(first_team), len(second_team))
        substrings_total_length = 0
        while True:
            s = SequenceMatcher(None, first_team, second_team)
            substring = s.find_longest_match(0, len(first_team), 0, len(second_team))
            if substring.size < 3:
                break
            substrings_total_length += substring.size
            first_team = first_team[:substring.a] + first_team[substring.a + substring.size:]
            second_team = second_team[:substring.b] + second_team[substring.b + substring.size:]

        similarity = substrings_total_length / min_initial_length
        return similarity


if __name__ == '__main__':
    m1 = Match(MatchTitle(['bmth', 'spassion']), [])
    m2 = Match(MatchTitle(['bring me the horizon', 'spassion']), [])
    similarity = Match._calculate_matches_similarity(m1, m2)
    print(similarity)
    print(m1.similar(m2, 0.6))
