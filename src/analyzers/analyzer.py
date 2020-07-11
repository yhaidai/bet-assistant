from pprint import pprint

from Sport import Sport
from abstract_grouper import AbstractGrouper
from syntax_formatters.esports.csgo.sample_data import favorit, parimatch, one_x_bet, ggbet, marathon


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
        # self.sports = []
        # for scraper, formatter in registry.items():
        #     bets = scraper.get_bets(sport_name)
        #     formatter.apply_unified_syntax_formatting(bets)
        #     self.sports.append(bets)

        self.sports = [
            Sport.from_dict(one_x_bet.sport),
            Sport.from_dict(parimatch.sport),
            Sport.from_dict(marathon.sport),
            Sport.from_dict(ggbet.sport),
            Sport.from_dict(favorit.sport),
            ]

        self.all_bets_sport = self.get_all_bets_sport()

    def get_all_bets_sport(self):
        all_matches = []
        for sport in self.sports:
            all_matches += sport.matches
        all_bets_sport = Sport(self.sports[0].name, all_matches)
        AbstractGrouper.group_matches(all_bets_sport)

        return all_bets_sport


if __name__ == '__main__':
    analyzer = Analyzer('csgo')
    s = analyzer.get_all_bets_sport()
    print(s)
