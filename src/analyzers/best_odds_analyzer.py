from analyzers.analyzer import Analyzer


class BestOddsAnalyzer(Analyzer):
    """
    Class for calculating best odds amongst all bookmakers odds
    """

    def get_best_odds_bets(self):
        """
        Get bets dictionary with specified best odds for each of the bets
        bets[match_title][bet_title] = odds -> bets[match_title][bet_title] = {best_odds_str: odds}
        """
        best_odds_bets = {}

        for match_title in self.all_bets.keys():
            best_odds_bets[match_title] = {}
            for bet_title, odds in self.all_bets[match_title].items():
                best_odds = max(odds.keys())
                best_odds_bets[match_title][bet_title] = {'*Max - ' + best_odds + '*': odds}

        return best_odds_bets
