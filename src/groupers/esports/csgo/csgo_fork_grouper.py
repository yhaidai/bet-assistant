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
    csgo = Sport.from_dict(ggbet_csgo_dict)
    grouper.group_bets(csgo)
    print(csgo)
