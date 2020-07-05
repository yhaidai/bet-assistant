from syntax_formatters.abstract_syntax_formatter import AbstractSyntaxFormatter


class OneXBetSyntaxFormatter(AbstractSyntaxFormatter):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the 1xbet website
    """
    _NAME = '1xbet'
    _INVALID_BET_TITLES = ('. ', '')

    def _get_name(self):
        return self._NAME

    def _get_invalid_bet_titles(self):
        return self._INVALID_BET_TITLES
