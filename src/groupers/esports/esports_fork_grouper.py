import re
from abc import ABC

from bet_group import BetGroup
from groupers.fork_grouper import ForkGrouper
from match_title_compiler import MatchTitleCompiler


class EsportsForkGrouper(ForkGrouper, ABC):
    _grouped_by = {
        r'^(\d-(st|nd|rd|th) map: )?.+? will (win)$': (3,),
        r'^(\d-(st|nd|rd|th) map: )?(.+?) will (win|lose)$': (3,),
        r'^(total maps) (over|under) (\d+(\.\d)?)$': (1, 3),
        r'^(total maps) (even|odd)$': (1,),
        r'^(\d-(st|nd|rd|th) map: )(correct score) \d+-\d+$': (3,),
        r'^(\d-(st|nd|rd|th) map: )?.+? will (not )?(win at least .+? map)': (4,),
    }

    def _get_handicap_targets(self) -> list:
        return ['maps']

    def _get_handicap_pattern_prefix(self):
        return r'^((?P<prefix>\d-(st|nd|rd|th) map: )?(?P<team_name>.+?) handicap (?P<sign>\+|-)(\d+(\.\d)?) ('

    def _get_grouped_by(self) -> dict:
        result = dict(EsportsForkGrouper._grouped_by)
        result.update(ForkGrouper._get_grouped_by(self))
        return result
