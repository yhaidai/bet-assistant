from pprint import pformat


class Sport:
    def __init__(self, name: str, matches: list):
        self.name = name
        self.matches = matches

    def _matches_dict(self):
        result = {}
        for match in self.matches:
            date_str = ''
            if match.date:
                date_str = match.date + ': '
            key = date_str + match.title + '(' + match.bookmaker + ' - ' + match.url + ')'
            result[key] = match.bets_dict()
        return result

    def __repr__(self):
        return pformat({self.name: self._matches_dict()})
