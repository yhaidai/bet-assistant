from difflib import SequenceMatcher

from match import Match
from match_title import MatchTitle


class MatchComparator:
    def __init__(self):
        self.similarities = {}

    def similar(self, first_match: Match, second_match: Match, certainty: float):
        similarity = self._calculate_matches_similarity(first_match, second_match, certainty)
        return similarity >= certainty

    def _calculate_matches_similarity(self, first_match: Match, second_match: Match, certainty: float):
        similarities = {}
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
                similarity = MatchComparator._calculate_teams_similarity(first_team, second_team)
                # print(similarity)
                if similarity > max_similarity:
                    max_similarity = similarity
                    max_similarity_second_team = second_team

            if len(first_team) == len(max_similarity_second_team):
                key = min(first_team, max_similarity_second_team)
                value = max(first_team, max_similarity_second_team)
            elif len(first_team) < len(max_similarity_second_team):
                key = first_team
                value = max_similarity_second_team
            else:
                key = max_similarity_second_team
                value = first_team

            similarities[key] = value
            total_similarity += max_similarity

            # print(teams1)
            # print(teams2_copy)
            # print(max_similarity_second_team)
            # print()
            teams2_copy.remove(max_similarity_second_team)

        relative_total_similarity = total_similarity / len(teams1)
        if relative_total_similarity >= certainty:
            self.similarities.update(similarities)
        
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
    comparator = MatchComparator()
    m1 = Match(MatchTitle(['illuminar', 'tikitakan']), '', [])
    m2 = Match(MatchTitle(['illuminar', 'tikitakan']), '', [])
    similarity = comparator._calculate_matches_similarity(m1, m2)
    print(similarity)
    print(comparator.similar(m1, m2, 0.6))
    print(comparator.similarities)
