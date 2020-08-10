from abc import ABC, abstractmethod


class AbstractScraper(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_matches_info_sport(self, sport_name):
        pass
