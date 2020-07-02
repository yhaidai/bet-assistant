from favorit_scraper import FavoritScraper
from favorit_syntax_formatter import FavoritSyntaxFormatter
from ggbet_scraper import GGBetScraper
from ggbet_syntax_formatter import GGBetSyntaxFormatter
from marathon_scraper import MarathonScraper
from marathon_syntax_formatter import MarathonSyntaxFormatter
from one_x_bet_scraper import OneXBetScraper
from one_x_bet_syntax_formatter import OneXBetSyntaxFormatter
from parimatch_scraper import ParimatchScraper
from parimatch_syntax_formatter import ParimatchSyntaxFormatter

registry = {
    OneXBetScraper(): OneXBetSyntaxFormatter(),
    FavoritScraper(): FavoritSyntaxFormatter(),
    MarathonScraper(): MarathonSyntaxFormatter(),
    GGBetScraper(): GGBetSyntaxFormatter(),
    ParimatchScraper(): ParimatchSyntaxFormatter(),
}
