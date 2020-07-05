from syntax_formatters.abstract_syntax_formatter import AbstractSyntaxFormatter


class GGBetSyntaxFormatter(AbstractSyntaxFormatter):
    _NAME = 'ggbet'

    def _get_name(self):
        return self._NAME
