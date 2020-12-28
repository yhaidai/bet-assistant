import os

from constants import SPORT_FULL_NAMES_TO_SHORT


def get_arbitrage_bets_xlsx_filename_by_full_sport_name(sport_full_name):
    return get_arbitrage_bets_xlsx_filename_by_short_sport_name(SPORT_FULL_NAMES_TO_SHORT[sport_full_name])


def get_arbitrage_bets_xlsx_filename_by_short_sport_name(sport_short_name):
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', 'arbitrager', 'sample_data',
            f'{sport_short_name}.xlsx'
        )
    )
