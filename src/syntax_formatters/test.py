from sample_data import parimatch, one_x_bet
from one_x_bet_syntax_formatter import OneXBetSyntaxFormatter
from parimatch_syntax_formatter import ParimatchSyntaxFormatter

formatter1 = OneXBetSyntaxFormatter(one_x_bet.bets)
formatter2 = ParimatchSyntaxFormatter(parimatch.bets)

bets1 = formatter1.bets
bets2 = formatter2.bets
c = 0
i = 0

for match_title in bets2.keys():
    for bet_title, odds in bets2[match_title].items():
        try:
            alternative_odds = bets1[match_title][bet_title]
            c += 1
            # print(match_title + '\n\t' + bet_title + ': ' + odds + ' - ' + alternative_odds)
        except KeyError:
            i += 1
            print(match_title + ' ---> ' + bet_title)
            continue

print(c)
print(i)
# print(bets1['winstrike - natus vincere junior']['1-st map: handicap winstrike -3.5'])
# print(bets2['winstrike - natus vincere junior']['1-st map: handicap winstrike -3.5'])
