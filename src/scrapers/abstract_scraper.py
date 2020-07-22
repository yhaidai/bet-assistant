from abc import ABC, abstractmethod


class AbstractScraper(ABC):
    @abstractmethod
    def get_matches_info_sport(self, sport_name):
        pass
