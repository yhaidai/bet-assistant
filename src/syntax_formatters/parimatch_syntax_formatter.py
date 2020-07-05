from syntax_formatters.abstract_syntax_formatter import AbstractSyntaxFormatter


class ParimatchSyntaxFormatter(AbstractSyntaxFormatter):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the parimatch website
    """
    _NAME = 'parimatch'

    def _get_name(self):
        return self._NAME

