import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from constants import sport_name
from scrapers.favorit_scraper import FavoritScraper
from scrapers.ggbet_scraper import GGBetScraper
from scrapers.marathon_scraper import MarathonScraper
from scrapers.one_x_bet_scraper import OneXBetScraper
from scrapers.parimatch_scraper import ParimatchScraper

scrapers = [ParimatchScraper(), OneXBetScraper(), GGBetScraper(), FavoritScraper(), MarathonScraper()]

t = time.time()
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(scraper.get_matches_info_sport, sport_name) for scraper in scrapers]
    for future in as_completed(futures):
        print(future.result())

for scraper in scrapers:
    scraper.renderer.quit()

print(time.time() - t)
