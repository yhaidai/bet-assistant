import re
import time
from pprint import pprint

from selenium.common.exceptions import NoSuchElementException

from one_x_bet_syntax_formatter import OneXBetSyntaxFormatter
from src.renderer.page import Page
from src.scrapers.abstract_scraper import AbstractScraper
from syntax_formatters.match_title_compiler import MatchTitleCompiler


class OneXBetScraper(AbstractScraper):
    _BASE_URL = 'https://1x-bet.com/en/'

    _SPORT_NAMES = {
        'csgo': 'CSGO',
        'dota 2': 'Dota-2',
    }
    _MENU = {
        'csgo': 'view-source:https://m.1x-bet-ua.com/en/line/Esports/'
    }

    def get_bets(self, sport_type):
        """
        Scrapes betting data for a given sport type

        :param sport_type: sport type to scrape betting data for
        :type sport_type: str
        """
        bets = {}
        match_urls = self.get_match_urls(sport_type)
        print(len(match_urls))

        for url in match_urls:
            bets.update(OneXBetScraper._get_bets(OneXBetScraper._BASE_URL + url))

        return bets

    @staticmethod
    def get_match_urls(sport_type):
        """
        Scrape match urls for a given sport type
        """
        match_urls = []
        page = Page(OneXBetScraper._MENU[sport_type])
        elements = re.split('[<>]', page.html)
        for el in elements:
            if OneXBetScraper._SPORT_NAMES[sport_type] in el and el.count('/') == 4:
                match_urls.append(el)

        return match_urls

    @staticmethod
    def _get_bets(match_url):
        """
        Scraps data such as match titles, bet titles and odds from the given match url

        :param match_url: any match url on the website
        :type match_url: str
        :return: bets dictionary in the following form:
        bets[match_title][bet_title] = odds
        :rtype: dict
        """
        print(match_url)
        bets = {}
        page = Page(match_url)
        OneXBetScraper.open_bets()

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
        """
        Scrapes match title from the current page

        :return: match title found on the page or None if nothing was found
        :rtype: str or None
        """
        team_names = [team.text for team in Page.driver.find_elements_by_class_name('team')]
        if not team_names:
            try:
                return Page.driver.find_element_by_class_name('name')
            except NoSuchElementException:
                return None
        return MatchTitleCompiler.compile_match_title(*team_names)

    @staticmethod
    def open_bets():
        """
        Open bets on the current page up, so hidden bet titles and odds can be scraped
        """
        elements = Page.driver.find_elements_by_class_name('bet-title')

        for element in elements:
            if element.get_attribute('class') == 'bet-title bet-title_justify min':
                Page.click(element)


if __name__ == '__main__':
    t = time.time()

    scraper = OneXBetScraper()
    # b = scraper.get_bets('csgo')
    b = scraper.get_formatted_bets('csgo')
    pprint(b)
    Page.driver.quit()

    print(time.time() - t)
