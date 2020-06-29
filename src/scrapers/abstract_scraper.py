from abc import ABC, abstractmethod


class AbstractScraper(ABC):
    def __init__(self, formatter):
        """
        Initialize scraper with corresponding syntax formatter

        :param formatter: formatter for specific website's scraper
        :type formatter: AbstractSyntaxFormatter
        """
        self.formatter = formatter

    def get_formatted_bets(self, sport_type):
        bets = self.get_bets(sport_type)
        self.formatter.apply_unified_syntax_formatting(bets)
        return self.formatter.bets

    @abstractmethod
    def get_bets(self, sport_type):
        """
        Scrapes betting data for a given sport type

        :param sport_type: sport type to scrape betting data for
        :type sport_type: str
        """
        pass
