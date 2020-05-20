import parimatch


class ParimatchSyntaxFormatter:
    def __init__(self, bets):
        self.bets = {match_title: {} for match_title in bets.keys()}
        self.apply_unified_syntax_formatting(bets)

    def apply_unified_syntax_formatting(self, bets):
        for match_title in bets.keys():
            for bet_title, odds in bets[match_title].items():
                self._format_total(match_title, bet_title, odds)

    def _format_total(self, match_title, bet_title, odds):
        if 'Total' in bet_title:
            sentences = bet_title.split('. ')
            temp = sentences[1]
            sentences[1] = sentences[2]
            sentences[2] = temp

            formatted_title = ''
            for s in sentences:
                formatted_title += s + ' '
            formatted_title = formatted_title.lower()[:-1]

            self.bets[match_title][formatted_title] = odds


formatter = ParimatchSyntaxFormatter(parimatch.bets)
# pprint(formatter.bets)
