from sport import Sport
from syntax_formatters.esports.lol.sample_data.favorit import sport as favorit_lol_dict
from groupers.esports.esports_fork_grouper import EsportsForkGrouper


class LoLForkGrouper(EsportsForkGrouper):
    _grouped_by = {
        r'(^\d-(st|nd|rd|th) map: )?(total (kills|dragons|barons|turrets|inhibitors)|duration) (over|under) (\d+('
        r'\.\d)?)$': (3, 6),
        r'(^\d-(st|nd|rd|th) map: )?(total kills) (even|odd)$': (3, ),
        r'(^\d-(st|nd|rd|th) map: ).+? (most kills)$': (3, ),
        r'(^\d-(st|nd|rd|th) map: ).+? (will first (kill (baron|dragon)|destroy (turret|inhibitor)))$': (3, ),
        r'(^\d-(st|nd|rd|th) map: ).+? (first blood|will make kill \d+)$': (3, ),
        r'(^\d-(st|nd|rd|th) map: ).+? (will first make \d+ kills)$': (3, ),
        }

    def _get_grouped_by(self) -> dict:
        result = dict(LoLForkGrouper._grouped_by)
        result.update(EsportsForkGrouper._get_grouped_by(self))
        return result

    def _get_handicap_targets(self):
        return EsportsForkGrouper._get_handicap_targets(self) + ['kills']


if __name__ == '__main__':
    grouper = LoLForkGrouper()
    lol = Sport.from_dict(favorit_lol_dict)
    grouped_lol = grouper.group_bets(lol)
    print(grouped_lol)
