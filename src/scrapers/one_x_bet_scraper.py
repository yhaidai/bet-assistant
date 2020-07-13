import os.path
import time
from pprint import pprint, pformat

from selenium.common.exceptions import NoSuchElementException

from Bet import Bet
from Match import Match
from Sport import Sport
from constants import sport_name
from match_title_compiler import MatchTitleCompiler
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

    def get_sport_bets(self, sport_name: str):
        sport_bets = []
        championships = OneXBetScraper._get_championships(sport_name)
        championship_urls = OneXBetScraper.get_championship_urls(championships)
        print(len(championship_urls))

        match_elements = OneXBetScraper._get_match_elements(championships)
        print('Match urls count: ' + str(len(match_elements)))
        match_urls = OneXBetScraper.get_match_urls(match_elements, championship_urls)

        match_urls = list(match_urls)[:20]
        for url in match_urls:
            full_url = OneXBetScraper._BASE_URL + url
            match_bets = OneXBetScraper._get_match_bets(full_url)
            if match_bets:
                sport_bets.append(match_bets)

        sport = Sport(sport_name, sport_bets)
        return sport

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

        menu = page.driver.find_element_by_class_name('liga_menu')

        pattern = OneXBetScraper._SPORT_NAMES[sport_name]
        selector = 'a[href*="' + pattern + '"]'

        championships = {el for el in menu.find_elements_by_css_selector(selector) if el.get_attribute('href').count(
            '/') == 7}

        return championships

    @staticmethod
    def get_match_urls(matches, championship_urls):
        base_len = len(OneXBetScraper._BASE_URL)
        return {m.get_attribute('href')[base_len:] for m in matches}.difference(championship_urls)

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
        event_menus = event_menus[:1]
        for event_menu in event_menus:
            for championship_url in championship_urls:
                css_link_prefix_match = 'a[href^="' + championship_url + '"]'
                try:
                    matches.update(el for el in menu.find_elements_by_css_selector(css_link_prefix_match))
                except NoSuchElementException:
                    pass

        return matches

    @staticmethod
    def _get_match_bets(match_url):
        """
        Scraps data such as match titles, bet titles and odds from the given url
        :param match_url: any valid match url on the website
        :type match_url: str
        :return: match bets
        :rtype: Match
        """
        match = None
        bets = []
        page = Page(match_url)
        OneXBetScraper._open_bets()

        print(match_url)
        match_title = OneXBetScraper._get_match_title()
        if not match_title:
            print('MATCH TITLE NOT FOUND')
            return match

        bet_groups = page.driver.find_elements_by_class_name('bet_group')
        for bet_group in bet_groups:
            bet_title = bet_group.find_element_by_class_name('bet-title').text
            if '\nSlider' in bet_title:
                bet_title = bet_title[:-len('\nSlider')]

            bet_types = [el.text for el in bet_group.find_elements_by_class_name('bet_type')]
            odds = [el.text for el in bet_group.find_elements_by_class_name('koeff')]

            for i in range(len(bet_types)):
                bet = Bet(bet_title + '. ' + bet_types[i], odds[i], OneXBetScraper._NAME, match_url)
                bets.append(bet)

        match = Match(match_title, bets)
        return match

    @staticmethod
    def _get_match_title():
        for container in OneXBetScraper._TEAM_NAME_CONTAINERS:
            team_names = [team.text for team in Page.driver.find_elements_by_class_name(container)]
            print(container)
            print(team_names)
            if team_names:
                break

        if not team_names:
            try:
                board_div = Page.driver.find_element_by_class_name('board_div')
                return board_div.find_element_by_class_name('name').text
            except NoSuchElementException:
                return None

        return MatchTitleCompiler.compile_match_title(*team_names)

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
    b = scraper.get_sport_bets(sport_name)
    pprint(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + sport_name + '\\one_x_bet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', pformat(b), file=f)
    print(time.time() - t)
