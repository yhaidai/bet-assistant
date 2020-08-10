from datetime import timedelta
from difflib import SequenceMatcher

from date_time import DateTime
from match import Match
from match_title import MatchTitle


class MatchComparator:
    def __init__(self):
        self.similarities = {}

    def similar(self, first_match: Match, second_match: Match, certainty: float):
        similarity = self.calculate_matches_similarity(first_match, second_match, certainty)
        return similarity >= certainty

    def calculate_matches_similarity(self, first_match: Match, second_match: Match, certainty: float):
        similarities = {}
        teams1 = first_match.title.teams
        teams2 = second_match.title.teams

        time_delta = abs(first_match.date_time - second_match.date_time)
        date_time_coefficient = 1 - time_delta / timedelta(seconds=45 * 60)
        if len(teams1) != len(teams2) or first_match.scraper == second_match.scraper or date_time_coefficient <= 0:
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
                key = max(first_team, max_similarity_second_team)
                value = min(first_team, max_similarity_second_team)
            elif len(first_team) < len(max_similarity_second_team):
                key = max_similarity_second_team
                value = first_team
            else:
                key = first_team
                value = max_similarity_second_team

            similarities[key] = value
            total_similarity += max_similarity
            # print(first_team, max_similarity_second_team, max_similarity)

            teams2_copy.remove(max_similarity_second_team)

        relative_total_similarity = total_similarity / len(teams1) * date_time_coefficient
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
            # print(first_team[substring.a:substring.b])
            first_team = first_team[:substring.a] + first_team[substring.a + substring.size:]
            second_team = second_team[:substring.b] + second_team[substring.b + substring.size:]

        similarity = substrings_total_length / min_initial_length
        return similarity


if __name__ == '__main__':
    certainty = 0.5
    comparator = MatchComparator()
    m1 = Match(MatchTitle(['invictus gaming', 'lynn vision']), '', DateTime(2000, 1, 1, 5), 1, [])
    m2 = Match(MatchTitle(['invictus gaming', 'tyloo']), '', DateTime(2000, 1, 1, 0), 2, [])
    similarity = comparator.calculate_matches_similarity(m1, m2, certainty)
    print(similarity)
    print(comparator.similar(m1, m2, certainty))
    print(comparator.similarities)
