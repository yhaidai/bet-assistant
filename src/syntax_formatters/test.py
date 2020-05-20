import one_x_bet
import parimatch
from one_x_bet_formatter import OneXBetSyntaxFormatter
from parimatch_syntax_formatter import ParimatchSyntaxFormatter

formatter1 = OneXBetSyntaxFormatter(one_x_bet.bets)
formatter2 = ParimatchSyntaxFormatter(parimatch.bets)

bets1 = formatter1.bets
bets2 = formatter2.bets

for match_title in bets1.keys():
    for bet_title, odds in bets1[match_title].items():
        try:
            alternative_odds = bets2[match_title][bet_title]
            # print('Found:\n\t' + match_title + '\n\t\t' + bet_title + ': ' + odds + ' - ' + alternative_odds)
        except KeyError:
            # print(match_title + ' ---> ' + bet_title)
            pass
