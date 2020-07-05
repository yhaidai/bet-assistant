from syntax_formatters.abstract_syntax_formatter import AbstractSyntaxFormatter


class FavoritSyntaxFormatter(AbstractSyntaxFormatter):
    _NAME = 'favorit'

    def _get_name(self):
        return self._NAME
