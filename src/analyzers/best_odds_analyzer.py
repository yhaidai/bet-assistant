from bet_group import BetGroup
from analyzers.analyzer import Analyzer


class BestOddsAnalyzer(Analyzer):
    """
    Class for calculating best odds amongst all bookmakers odds
    """

    def get_best_odds_bets_sport(self):
        for match in self.all_bets_sport:
            group = {}

            for bet in match:
                group.setdefault(bet.title, BetGroup(bet.title)).append(bet)

            for bet in list(match):
                if bet is not max(group[bet.title].bets):
                    match.bets.remove(bet)

        return self.all_bets_sport


if __name__ == '__main__':
    analyzer = BestOddsAnalyzer('csgo')
    s = analyzer.get_best_odds_bets_sport()
    print(s)
