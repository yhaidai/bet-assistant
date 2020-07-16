from abc import ABC

from groupers.fork_grouper import ForkGrouper
from sport import Sport
from syntax_formatters.football.sample_data.favorit import sport as favorit_football_dict


class FootballForkGrouper(ForkGrouper, ABC):
    _grouped_by = {
        r'^(\d-(st|nd|rd|th) half )?.+? will (win)$': (3,),
        r'^(\d-(st|nd|rd|th) half )?(draw) will (win|lose)$': (3,),
        r'^(\d-(st|nd|rd|th) half )?((.+? )?(asian )?total (goals|yellow cards|corners)) (over|under) (\d+(\.\d{1,'
        r'2})?)$': (3, 8),
        r'^(\d-(st|nd|rd|th) half )?(total goals|) (even|odd)$': (3,),
        r'^(\d-(st|nd|rd|th) half: )(correct score) \d+-\d+$': (3,),
    }

    def _get_handicap_targets(self) -> list:
        return ['goals', 'corners', 'yellow cards']

    def _get_handicap_pattern_prefix(self) -> str:
        return r'^((?P<prefix>\d-(st|nd|rd|th) half )?(?P<team_name>.+?) ' \
               r'(asian )?handicap (?P<sign>\+|-|)(\d+(\.\d{1,2})?) ('

    def _get_grouped_by(self) -> dict:
        result = dict(FootballForkGrouper._grouped_by)
        result.update(ForkGrouper._get_grouped_by(self))
        return result


if __name__ == '__main__':
    grouper = FootballForkGrouper()
    football = Sport.from_dict(favorit_football_dict)
    grouped_football = grouper.group_bets(football)
    print(grouped_football)
