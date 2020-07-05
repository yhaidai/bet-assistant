from favorit_scraper import FavoritScraper
from esports.csgo.favorit_syntax_formatter import FavoritSyntaxFormatter
from ggbet_scraper import GGBetScraper
from esports.csgo.ggbet_syntax_formatter import GGBetSyntaxFormatter
from marathon_scraper import MarathonScraper
from esports.csgo.marathon_syntax_formatter import MarathonSyntaxFormatter
from one_x_bet_scraper import OneXBetScraper
from esports.csgo.one_x_bet_syntax_formatter import OneXBetSyntaxFormatter
from parimatch_scraper import ParimatchScraper
from esports.csgo.parimatch_syntax_formatter import ParimatchSyntaxFormatter

registry = {
    OneXBetScraper(): OneXBetSyntaxFormatter(),
    FavoritScraper(): FavoritSyntaxFormatter(),
    MarathonScraper(): MarathonSyntaxFormatter(),
    GGBetScraper(): GGBetSyntaxFormatter(),
    ParimatchScraper(): ParimatchSyntaxFormatter(),
    }
