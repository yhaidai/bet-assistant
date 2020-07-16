from sport import Sport
from syntax_formatters.esports.dota.sample_data.marathon import sport as marathon_dota_dict
from groupers.esports.esports_fork_grouper import EsportsForkGrouper


class DotaForkGrouper(EsportsForkGrouper):
    _grouped_by = {
        r'(^\d-(st|nd|rd|th) map: )?(total (kills|roshans)|duration) (over|under) (\d+(\.\d)?)$': (3, 5),
        r'(^\d-(st|nd|rd|th) map: )?(total kills) (even|odd)$': (3, ),
        r'(^\d-(st|nd|rd|th) map: )(megacreeps) (yes|no)$': (3, ),
        r'(^\d-(st|nd|rd|th) map: ).+? (will first (kill roshan|lose barracks|destroy tower))$': (3, ),
        r'(^\d-(st|nd|rd|th) map: ).+? (first blood|will make kill \d+)$': (3, ),
        r'(^\d-(st|nd|rd|th) map: ).+? (will first make \d+ kills)$': (3, ),
        }

    def _get_grouped_by(self) -> dict:
        result = dict(DotaForkGrouper._grouped_by)
        result.update(EsportsForkGrouper._get_grouped_by(self))
        return result

    def _get_handicap_targets(self):
        return EsportsForkGrouper._get_handicap_targets(self) + ['kills']


if __name__ == '__main__':
    grouper = DotaForkGrouper()
    dota = Sport.from_dict(marathon_dota_dict)
    grouped_dota = grouper.group_bets(dota)
    print(grouped_dota)
