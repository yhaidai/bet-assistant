from abc import ABC, abstractmethod


class AbstractScraper(ABC):
    @abstractmethod
    def get_bets(self, sport_type):
        """
        Scrapes betting data for a given sport type

        :param sport_type: sport type to scrape betting data for
        :type sport_type: str
        """
        pass
