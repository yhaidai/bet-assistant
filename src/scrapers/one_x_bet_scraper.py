import time
from pprint import pprint, pformat
import os.path
from selenium.common.exceptions import NoSuchElementException

from match_title_compiler import MatchTitleCompiler
from src.renderer.page import Page
from src.scrapers.abstract_scraper import AbstractScraper


class OneXBetScraper(AbstractScraper):
    base_url = 'https://1x-bet.com/en/'
    sport_names = {
        'csgo': 'CSGO',
        'dota 2': 'Dota-2',
        }
    menu = {
        'csgo': 'line/Esports/'
        }

    def get_bets(self, sport_type):
        bets = {}
        championships = OneXBetScraper._get_championships(sport_type)
        championship_urls = OneXBetScraper.get_championship_urls(championships)

        matches = OneXBetScraper._get_matches(championships)
        match_urls = OneXBetScraper.get_match_urls(matches, championship_urls)
        size = len(match_urls)
        for i in range(size - 30):
            match_urls.pop()
        print(len(match_urls))

        for url in match_urls:
            bets.update(OneXBetScraper._get_bets(OneXBetScraper.base_url + url))

        return bets

    @staticmethod
    def get_championship_urls(championships):
        base_len = len(OneXBetScraper.base_url)
        return [ch.get_attribute('href')[base_len:] for ch in championships]

    @staticmethod
    def _get_championships(sport_type):
        page = Page(OneXBetScraper.base_url)
        sport = page.driver.find_element_by_css_selector('a[href^="' + OneXBetScraper.menu[sport_type] + '"]')
        page.click(sport)
        time.sleep(2)

        menu = page.driver.find_element_by_class_name('liga_menu')

        pattern = OneXBetScraper.sport_names[sport_type]
        selector = 'a[href*="' + pattern + '"]'

        championships = {el for el in menu.find_elements_by_css_selector(selector)}

        return championships

    @staticmethod
    def get_match_urls(matches, championship_urls):
        base_len = len(OneXBetScraper.base_url)
        return {m.get_attribute('href')[base_len:] for m in matches}.difference(championship_urls)

    @staticmethod
    def _get_matches(championships):
        matches = set()
        menu = Page.driver.find_element_by_class_name('liga_menu')
        championship_urls = OneXBetScraper.get_championship_urls(championships)

        OneXBetScraper.open_championships(championships)

        event_menus = menu.find_elements_by_class_name('event_menu')
        for event_menu in event_menus:
            for championship_url in championship_urls:
                css_link_prefix_match = 'a[href^="' + championship_url + '"]'

                try:
                    matches.update(el for el in menu.find_elements_by_css_selector(css_link_prefix_match))
                except NoSuchElementException:
                    pass

        return matches

    @staticmethod
    def _get_bets(match_url):
        """
        Scraps data such as match titles, bet titles and odds from the given url
        :param match_url: any valid match url on the website
        :type match_url: str
        :return: bets dictionary in the following form:
        bets[match_title][bet_title] = odds
        :rtype: dict
        """
        bets = {}
        page = Page(match_url)
        OneXBetScraper.open_bets()

        print(match_url)
        match_title = OneXBetScraper._get_match_title()
        if not match_title:
            return bets
        bets[match_title] = {}

        bet_groups = page.driver.find_elements_by_class_name('bet_group')
        for bet_group in bet_groups:
            bet_title = bet_group.find_element_by_class_name('bet-title').text
            if '\nSlider' in bet_title:
                bet_title = bet_title[:-len('\nSlider')]

            bet_types = [el.text for el in bet_group.find_elements_by_class_name('bet_type')]
            odds = [el.text for el in bet_group.find_elements_by_class_name('koeff')]
            for i in range(len(bet_types)):
                bets[match_title][bet_title + '. ' + bet_types[i]] = odds[i]

        return bets

    @staticmethod
    def _get_match_title():
        team_names = [team.text for team in Page.driver.find_elements_by_class_name('team')]
        if not team_names:
            try:
                return Page.driver.find_element_by_class_name('name')
            except NoSuchElementException:
                return None
        return MatchTitleCompiler.compile_match_title(*team_names)

    @staticmethod
    def open_championships(championships):
        for championship in championships:
            Page.click(championship)

    @staticmethod
    def open_bets():
        elements = Page.driver.find_elements_by_class_name('bet-title')

        for element in elements:
            if element.get_attribute('class') == 'bet-title bet-title_justify min':
                Page.click(element)


if __name__ == '__main__':
    t = time.time()

    scraper = OneXBetScraper()
    b = scraper.get_bets('csgo')
    pprint(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\one_x_bet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('bets = ', pformat(b), file=f)
    print(time.time() - t)
