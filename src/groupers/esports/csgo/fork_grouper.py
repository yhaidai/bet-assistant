import re

from Sport import Sport
from syntax_formatters.esports.csgo.sample_data.ggbet import sport as ggbet_csgo_dict
from groupers.esports.abstract_grouper import AbstractGrouper


class ForkGrouper(AbstractGrouper):
    _grouped_by = {
        r'(^\d-.{2} map: )?.+? will (win in round \d+)$': (2, ),
        }

    def _get_grouped_by(self):
        return self._grouped_by


if __name__ == '__main__':
    grouper = ForkGrouper()
    csgo = Sport.from_dict(ggbet_csgo_dict)
    grouped_csgo = grouper.group_bets(csgo)
    print(grouped_csgo)
