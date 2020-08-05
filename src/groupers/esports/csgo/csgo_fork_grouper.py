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
        r'(^\d-(st|nd|rd|th) map: )?(total rounds) (even|odd)$': (3, ),
        r'(^\d-(st|nd|rd|th) map: )?.+? will (win in round \d+)$': (3, ),
        r'(^\d-(st|nd|rd|th) map: )(overtime) (yes|no)$': (3, ),
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
        Match(MatchTitle(['forze', 'sg.pro']), 'parimatch', DateTime(2020, 8, 6, 14, 0, 0), 1, []),
        Match(MatchTitle(['forze', 'sg.pro']), '1xbet', DateTime(2020, 8, 6, 14, 0, 0), 2, []),
        Match(MatchTitle(['forze', 's-gaming']), 'favorit', DateTime(2020, 8, 6, 14, 0, 0), 3, []),
        Match(MatchTitle(['forze', 's-gaming']), 'ggbet', DateTime(2020, 8, 6, 14, 0, 0), 4, []),
    ])
    groups = grouper.get_match_groups(csgo)
    pprint(groups)
