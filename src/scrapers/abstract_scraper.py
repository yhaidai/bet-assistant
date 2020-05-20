from abc import ABC, abstractmethod


class AbstractScraper(ABC):
    @abstractmethod
    def get_bets(self, sport_type):
        pass
