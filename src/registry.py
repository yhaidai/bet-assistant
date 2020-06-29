from one_x_bet_scraper import OneXBetScraper
from one_x_bet_syntax_formatter import OneXBetSyntaxFormatter
from parimatch_scraper import ParimatchScraper
from parimatch_syntax_formatter import ParimatchSyntaxFormatter

registry = {
    ParimatchScraper(): ParimatchSyntaxFormatter(),
    OneXBetScraper(): OneXBetSyntaxFormatter()
}
