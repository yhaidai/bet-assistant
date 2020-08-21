from pprint import pprint

from date_time import DateTime
from match import Match
from match_title import MatchTitle
from sport import Sport
from syntax_formatters.esports.csgo.sample_data.ggbet import sport as ggbet_csgo_dict
from groupers.esports.esports_fork_grouper import EsportsForkGrouper


class CSGOForkGrouper(EsportsForkGrouper):
    _grouped_by = {
        r'(^\d-(st|nd|rd|th) map: )?(total rounds) (over|under) (\d+(\.\d)?)$': (3, 5),
        r'(^\d-(st|nd|rd|th) map: )?(total rounds) (even|odd)$': (3,),
        r'(^\d-(st|nd|rd|th) map: )?.+? will (win in round \d+)$': (3,),
        r'(^\d-(st|nd|rd|th) map: )(overtime) (yes|no)$': (3,),
        r'(^\d-(st|nd|rd|th) map: )(total kills in round \d+ )(over |under )(\d+(\.\d))$': (3, 5),
        }

    def _get_grouped_by(self) -> dict:
        result = dict(CSGOForkGrouper._grouped_by)
        result.update(EsportsForkGrouper._get_grouped_by(self))
        return result

    def _get_handicap_targets(self):
        return EsportsForkGrouper._get_handicap_targets(self) + ['rounds']


class OneXBetScraper:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OneXBetScraper, cls).__new__(cls)
        return cls.instance

    def get_name(self):
        return '1xbet'


class ParimatchScraper:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ParimatchScraper, cls).__new__(cls)
        return cls.instance

    def get_name(self):
        return '1xbet'


class FavoritScraper:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FavoritScraper, cls).__new__(cls)
        return cls.instance

    def get_name(self):
        return '1xbet'


class MarathonScraper:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MarathonScraper, cls).__new__(cls)
        return cls.instance

    def get_name(self):
        return '1xbet'


class GGBetScraper:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GGBetScraper, cls).__new__(cls)
        return cls.instance

    def get_name(self):
        return '1xbet'


if __name__ == '__main__':
    grouper = CSGOForkGrouper()
    csgo = Sport('csgo', [
        Match(MatchTitle(['Top Esports', 'Suning Gaming']),
              'https://1x-bet.com/en/line/Esports/1309773-League-of-Legends-LPL-Summer-Playoffs/81469989-Top-Esports-Suning-Gaming/',
              DateTime(2020, 8, 9, 19, 0, 0), OneXBetScraper(), []),
        Match(MatchTitle(['Top', 'Sunning']),
              'https://www.parimatch.com/en/sport/kibersport/liga-legend-lpl',
              DateTime(2020, 8, 9, 19, 0, 0), ParimatchScraper(), []),
        Match(MatchTitle(['Top Esports', 'SN Gaming']),
              'https://www.favorit.com.ua/en/bets/#event=27802672&tours=182350,776347,776418,792747,977780,1011803,1037535,1061879,1258082,1265594,1293917,1618224,1713907,2270463',
              DateTime(2020, 8, 9, 19, 0, 0), FavoritScraper(), []),
        Match(MatchTitle(['Suning Gaming', 'Top Esports']),
              'https://www.marathonbet.com/en/betting/e-Sports/LoL/LPL+Summer/Main+Event/Best+of+5+maps/Suning+Gaming+vs+Top+Esports+-+9994779',
              DateTime(2020, 8, 9, 19, 0, 0), MarathonScraper(), []),
        Match(MatchTitle(['Top Esports', 'Suning Gaming']),
              'https://gg.bet/en/betting/match/top-esports-vs-suning-gaming-22-08',
              DateTime(2020, 8, 9, 19, 0, 0), GGBetScraper(), []),
        ])
    groups = grouper.get_match_groups(csgo)
    pprint(groups)
