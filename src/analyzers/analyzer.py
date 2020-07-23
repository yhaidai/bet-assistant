from pprint import pprint

from match import Match
from registry import registry
from sport import Sport
from fork_grouper import ForkGrouper
from syntax_formatters.esports.csgo.sample_data import favorit, parimatch, one_x_bet, ggbet, marathon
# from syntax_formatters.esports.dota.sample_data import favorit, parimatch, one_x_bet, ggbet, marathon
# from syntax_formatters.esports.lol.sample_data import favorit, parimatch, one_x_bet, ggbet, marathon
# from syntax_formatters.football.sample_data import favorit, parimatch, one_x_bet, ggbet, marathon


class Analyzer:
    """
    Class for collecting betting info and analyzing it
    """

    def __init__(self, sport_name: str):
        """
        Scrape betting info on a given sport type

        :param sport_name: sport name e.g. 'csgo', 'dota'
        :type sport_name: str
        """
        self.sports = []
        for scraper, formatter in registry.items():
            sport = scraper.get_matches_info_sport(sport_name)
            self.sports.append(sport)
        # self.sports = [
        #     Sport.from_dict(one_x_bet.sport),
        #     Sport.from_dict(parimatch.sport),
        #     Sport.from_dict(marathon.sport),
        #     Sport.from_dict(ggbet.sport),
        #     Sport.from_dict(favorit.sport),
        #     ]

        self.all_bets_sport = self.get_all_bets_sport()

    def get_all_bets_sport(self) -> Sport:
        all_matches = []
        for sport in self.sports:
            all_matches += sport.matches
        all_matches_sport = Sport(self.sports[0].name, all_matches)
        self._scrape_bets(all_matches_sport)

        return all_matches_sport

    @staticmethod
    def _scrape_bets(all_matches_sport):
        match_groups = ForkGrouper.get_match_groups(all_matches_sport)
        pprint(match_groups)
        for title, group in match_groups.items():
            all_bets = []
            for match in group:
                match.scraper.scrape_match_bets(match)
                print('\n' * 5)
                print(match.bets)
                print('\n' * 5)
                all_bets += match.bets
                all_matches_sport.matches.remove(match)
                formatter = registry[match.scraper][all_matches_sport.name]
                formatter.format_match(match)

            all_bets_match = Match(title, '', '', all_bets)
            all_matches_sport.matches.append(all_bets_match)
            # TODO: dispatch group


if __name__ == '__main__':
    analyzer = Analyzer('csgo')
    s = analyzer.get_all_bets_sport()
    print(s)
