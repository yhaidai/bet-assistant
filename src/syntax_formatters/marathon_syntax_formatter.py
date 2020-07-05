from syntax_formatters.abstract_syntax_formatter import AbstractSyntaxFormatter


class MarathonSyntaxFormatter(AbstractSyntaxFormatter):
    _NAME = 'marathon'

    def _get_name(self):
        return self._NAME
