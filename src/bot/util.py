import os

from constants import SPORT_FULL_NAMES_TO_SHORT


def get_arbitrage_bets_xlsx_filename(sport_full_name):
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', 'arbitrager', 'sample_data',
            f'{SPORT_FULL_NAMES_TO_SHORT[sport_full_name]}.xlsx'
        )
    )
