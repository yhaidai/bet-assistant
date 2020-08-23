from abc import ABC, abstractmethod
from threading import Lock

from scrapers.renderer.renderer import Renderer


class AbstractScraper(ABC):
    __subclass_instances = []
    __subclasses_to_renderers_lock = Lock()

    def __init__(self):
        self.renderer = Renderer()
        with AbstractScraper.__subclasses_to_renderers_lock:
            if self not in AbstractScraper.__subclass_instances:
                AbstractScraper.__subclass_instances.append(self)

    def __new__(cls):
        for subclass_instance in AbstractScraper.__subclass_instances:
            if subclass_instance.__class__.__name__ == cls.__name__:
                return subclass_instance
        return super(AbstractScraper, cls).__new__(cls)

    def __reduce__(self):
        return self.__class__, ()

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_matches_info_sport(self, sport_name):
        pass
