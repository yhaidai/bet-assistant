from favorit_scraper import FavoritScraper
from syntax_formatters.esports.csgo.csgo_favorit_syntax_formatter import CSGOFavoritSyntaxFormatter
from syntax_formatters.esports.dota.dota_favorit_syntax_formatter import DotaFavoritSyntaxFormatter
from syntax_formatters.esports.lol.lol_favorit_syntax_formatter import LoLFavoritSyntaxFormatter
from syntax_formatters.football.football_favorit_syntax_formatter import FootballFavoritSyntaxFormatter
from ggbet_scraper import GGBetScraper
from syntax_formatters.esports.csgo.csgo_ggbet_syntax_formatter import CSGOGGBetSyntaxFormatter
from syntax_formatters.esports.dota.dota_ggbet_syntax_formatter import DotaGGBetSyntaxFormatter
from syntax_formatters.esports.lol.lol_ggbet_syntax_formatter import LoLGGBetSyntaxFormatter
from syntax_formatters.football.football_ggbet_syntax_formatter import FootballGGBetSyntaxFormatter
from marathon_scraper import MarathonScraper
from syntax_formatters.esports.csgo.csgo_marathon_syntax_formatter import CSGOMarathonSyntaxFormatter
from syntax_formatters.esports.dota.dota_marathon_syntax_formatter import DotaMarathonSyntaxFormatter
from syntax_formatters.esports.lol.lol_marathon_syntax_formatter import LoLMarathonSyntaxFormatter
from syntax_formatters.football.football_marathon_syntax_formatter import FootballMarathonSyntaxFormatter
from one_x_bet_scraper import OneXBetScraper
from syntax_formatters.esports.csgo.csgo_one_x_bet_syntax_formatter import CSGOOneXBetSyntaxFormatter
from syntax_formatters.esports.dota.dota_one_x_bet_syntax_formatter import DotaOneXBetSyntaxFormatter
from syntax_formatters.esports.lol.lol_one_x_bet_syntax_formatter import LoLOneXBetSyntaxFormatter
from syntax_formatters.football.football_one_x_bet_syntax_formatter import FootballOneXBetSyntaxFormatter
from parimatch_scraper import ParimatchScraper
from syntax_formatters.esports.csgo.csgo_parimatch_syntax_formatter import CSGOParimatchSyntaxFormatter
from syntax_formatters.esports.dota.dota_parimatch_syntax_formatter import DotaParimatchSyntaxFormatter
from syntax_formatters.esports.lol.lol_parimatch_syntax_formatter import LoLParimatchSyntaxFormatter
from syntax_formatters.football.football_parimatch_syntax_formatter import FootballParimatchSyntaxFormatter

registry = {
    ParimatchScraper(): {
        'csgo': CSGOParimatchSyntaxFormatter(),
        'dota': DotaParimatchSyntaxFormatter(),
        'lol': LoLParimatchSyntaxFormatter(),
        'football': FootballParimatchSyntaxFormatter(),
        },
    OneXBetScraper(): {
        'csgo': CSGOOneXBetSyntaxFormatter(),
        'dota': DotaOneXBetSyntaxFormatter(),
        'lol': LoLOneXBetSyntaxFormatter(),
        'football': FootballOneXBetSyntaxFormatter(),
        },
    GGBetScraper(): {
        'csgo': CSGOGGBetSyntaxFormatter(),
        'dota': DotaGGBetSyntaxFormatter(),
        'lol': LoLGGBetSyntaxFormatter(),
        'football': FootballGGBetSyntaxFormatter(),
        },
    FavoritScraper(): {
        'csgo': CSGOFavoritSyntaxFormatter(),
        'dota': DotaFavoritSyntaxFormatter(),
        'lol': LoLFavoritSyntaxFormatter(),
        'football': FootballFavoritSyntaxFormatter(),
        },
    MarathonScraper(): {
        'csgo': CSGOMarathonSyntaxFormatter(),
        'dota': DotaMarathonSyntaxFormatter(),
        'lol': LoLMarathonSyntaxFormatter(),
        'football': FootballMarathonSyntaxFormatter(),
        },
    }
