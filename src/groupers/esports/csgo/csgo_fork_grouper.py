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


if __name__ == '__main__':
    grouper = CSGOForkGrouper()
    csgo = Sport('csgo', [
        Match(MatchTitle(['cloud9', 'team one']),
              'https://1x-bet.com/en/line/Football/206667-Finland-Ykkonen-Division-1/80859226-SJK-Akatemia-Mikkelin-Palloilijat/',
              DateTime(2020, 8, 9, 19, 0, 0), 2, []),
        Match(MatchTitle(['cloud9', 'teamone']),
              'https://www.parimatch.com/en/sport/futbol/finljandija-ykkonen',
              DateTime(2020, 8, 9, 19, 0, 0), 1, []),
        Match(MatchTitle(['cloud9', 'team one']),
              'https://www.favorit.com.ua/en/bets/#event=27648297&tours=18755,18811,19139',
              DateTime(2020, 8, 9, 19, 0, 0), 3, []),
        Match(MatchTitle(['cloud9', 'team one']),
              'https://www.marathonbet.com/en/betting/Football/Finland/Veikkausliiga/Honka+vs+SJK+-+9926868',
              DateTime(2020, 8, 9, 19, 0, 0), 0, []),

        Match(MatchTitle(['cloud9', 'team one']),
              'https://1x-bet.com/en/line/Esports/2109602-Dota-2-Movistar-Liga-Pro-Gaming-Season-5/80852466-Infamous'
              '-Omega-Gaming/1',
              DateTime(2020, 8, 8, 21, 0, 0), 2, []),
        Match(MatchTitle(['cloud9', 'teamone']),
              'https://www.parimatch.com/en/sport/kibersport/dota-2-movistar-lpg1',
              DateTime(2020, 8, 8, 21, 0, 0), 1, []),
        Match(MatchTitle(['cloud9', 'team one']),
              'https://www.favorit.com.ua/en/bets/#event=27623202&tours=631831,1127880,1193929,1747127,1939467,'
              '2461097,2515710,2520056,25236781',
              DateTime(2020, 8, 8, 21, 0, 0), 3, []),
        Match(MatchTitle(['cloud9', 'team one']),
              'https://www.marathonbet.com/en/betting/e-Sports/CS%3AGO/DreamHack+Open/Main+Event/Best+of+3+maps'
              '/Cloud9+vs+Team+One+-+99333191',
              DateTime(2020, 8, 8, 21, 0, 0), 0, []),
        Match(MatchTitle(['cloud9', 'team one']),
              'https://gg.bet/en/betting/match/infamous-vs-omega-gaming-06-081',
              DateTime(2020, 8, 8, 21, 0, 0), 4, []),
        ])
    groups = grouper.get_match_groups(csgo)
    pprint(groups)
