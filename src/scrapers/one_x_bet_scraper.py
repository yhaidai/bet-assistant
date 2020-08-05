import os.path
import time

from selenium.common.exceptions import NoSuchElementException

from bet import Bet
from date_time import DateTime
from match import Match
from match_title import MatchTitle
from sport import Sport
from constants import sport_name
from src.renderer.page import Page
from src.scrapers.abstract_scraper import AbstractScraper


class OneXBetScraper(AbstractScraper):
    _NAME = '1xbet'
    _BASE_URL = 'https://1x-bet.com/en/'
    _SPORT_NAMES = {
        'csgo': 'CSGO',
        'dota': 'Dota-2',
        'football': 'Football',
        'lol': 'League-of-Legends',
        }
    _MENU = {
        'csgo': 'line/Esports/',
        'dota': 'line/Esports/',
        'football': 'line/Football/',
        'lol': 'line/Esports/',
        }
    _TEAM_NAME_CONTAINERS = ['c-scoreboard-team__name-link', 'team', ]

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OneXBetScraper, cls).__new__(cls)
        return cls.instance

    def get_matches_info_sport(self, sport_name):
        championships = OneXBetScraper._get_championships(sport_name)
        championship_urls = OneXBetScraper.get_championship_urls(championships)
        print(len(championship_urls))

        match_elements = OneXBetScraper._get_match_elements(championships)
        sport_matches = self._get_matches_info(match_elements, championship_urls)

        sport = Sport(sport_name, sport_matches)
        return sport

    def _get_matches_info(self, match_elements, championship_urls):
        matches = []
        base_len = len(OneXBetScraper._BASE_URL)

        for match_element in list(match_elements)[:]:
            url = match_element.get_attribute('href')[base_len:]
            if url in championship_urls:
                continue
            match_title_text = match_element.find_element_by_class_name('gname').text
            match_title = MatchTitle.from_str(match_title_text)
            date_time_str = match_element.find_element_by_class_name('date').text
            date_time = DateTime.from_1xbet_str(date_time_str)
            match = Match(match_title, self._BASE_URL + url, date_time, self)
            matches.append(match)

        return matches

    @staticmethod
    def scrape_match_bets(match: Match):
        page = Page(match.url)
        OneXBetScraper._open_bets()

        bet_groups = page.driver.find_elements_by_class_name('bet_group')
        for bet_group in bet_groups:
            bet_title = bet_group.find_element_by_class_name('bet-title').text
            if '\nSlider' in bet_title:
                bet_title = bet_title[:-len('\nSlider')]

            bet_types = [el.text for el in bet_group.find_elements_by_class_name('bet_type')]
            odds = [el.text for el in bet_group.find_elements_by_class_name('koeff')]

            for i in range(len(bet_types)):
                bet = Bet(bet_title + '. ' + bet_types[i], odds[i], OneXBetScraper._NAME, match.url)
                match.bets.append(bet)

    @staticmethod
    def get_championship_urls(championships):
        base_len = len(OneXBetScraper._BASE_URL)
        return [ch.get_attribute('href')[base_len:] for ch in championships]

    @staticmethod
    def _get_championships(sport_name):
        page = Page(OneXBetScraper._BASE_URL)
        sport = page.driver.find_element_by_css_selector('a[href^="' + OneXBetScraper._MENU[sport_name] + '"]')
        page.click(sport)
        time.sleep(2)

        try:
            menu = page.driver.find_element_by_class_name('liga_menu')
        except NoSuchElementException:
            print('Caught NoSuchElementException("liga-menu"), retrying...')
            return OneXBetScraper._get_championships(sport_name)

        pattern = OneXBetScraper._SPORT_NAMES[sport_name]
        selector = 'a[href*="' + pattern + '"]'

        championships = {el for el in menu.find_elements_by_css_selector(selector) if el.get_attribute('href').count(
            '/') == 7}

        return championships

    @staticmethod
    def _get_match_elements(championships):
        matches = set()
        menu = Page.driver.find_element_by_class_name('liga_menu')
        championship_urls = OneXBetScraper.get_championship_urls(championships)

        print('Opening championships...')
        OneXBetScraper._open_championships(championships)

        print('Retrieving matches...')
        event_menus = menu.find_elements_by_class_name('event_menu')
        print('Event menus count: ' + str(len(event_menus)))
        for event_menu in event_menus:
            for championship_url in championship_urls:
                css_link_prefix_match = 'a[href^="' + championship_url + '"]'
                try:
                    matches.update(el for el in menu.find_elements_by_css_selector(css_link_prefix_match))
                except NoSuchElementException:
                    pass

        return matches

    @staticmethod
    def _open_championships(championships):
        for championship in championships:
            Page.click(championship)

    @staticmethod
    def _open_bets():
        elements = Page.driver.find_elements_by_class_name('bet-title')

        for element in elements:
            if element.get_attribute('class') == 'bet-title bet-title_justify min':
                Page.click(element)


if __name__ == '__main__':
    t = time.time()
    scraper = OneXBetScraper()

    sport = scraper.get_matches_info_sport(sport_name)
    for match in sport:
        scraper.scrape_match_bets(match)
    print(sport)

    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + sport_name + '\\one_x_bet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', sport, file=f)
    print(time.time() - t)
