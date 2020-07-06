from pprint import pprint, pformat
import os.path

from Bet import Bet
from Match import Match
from Sport import Sport
from abstract_scraper import AbstractScraper
import time

from constants import sport_name
from match_title_compiler import MatchTitleCompiler
from src.renderer.page import Page


class FavoritScraper(AbstractScraper):
    _NAME = 'favorit'
    _BASE_URL = 'https://www.favorit.com.ua/en/bets/#'
    _MENU = {
        'csgo': 'Counter-Strike: Global Offensive',
        'dota': 'Dota 2'
        }

    def get_sport_bets(self, sport_name):
        """
        Scrapes betting data for a given sport type

        :param sport_name: sport type to scrape betting data for
        :type sport_name: str
        """
        sport_bets = []
        match_buttons = self.get_match_buttons(sport_name)

        for match_button in match_buttons:
            match_bets = FavoritScraper._get_bets(match_button)
            if match_bets:
                sport_bets.append(match_bets)

        sport = Sport(sport_name, sport_bets)
        return sport

    @staticmethod
    def get_match_buttons(sport_name):
        """
        Scrape match buttons for a given sport type
        """
        page = Page(FavoritScraper._BASE_URL)

        headers = page.driver.find_elements_by_class_name('sport--name--head')
        for header in headers:
            if header.get_attribute('class') == 'sport--name--head sp_85':
                cybersports = header
        time.sleep(0.25)
        page.click(cybersports)
        time.sleep(0.25)
        drop_down_menu = cybersports.parent.find_element_by_class_name('slideInDown')
        checkboxes = drop_down_menu.find_elements_by_tag_name('b')
        titles = drop_down_menu.find_elements_by_class_name('ttt')
        # print(checkboxes)

        for i in range(len(checkboxes)):
            if titles[i].get_attribute('innerHTML') == FavoritScraper._MENU[sport_name]:
                page.click(checkboxes[i])
        time.sleep(0.25)

        main_table = page.driver.find_element_by_class_name('column--container')
        time.sleep(1)
        buttons = main_table.find_elements_by_class_name('event--more')
        # print(len(buttons))

        return buttons

    @staticmethod
    def _get_bets(match_button):
        Page.click(match_button)
        time.sleep(0.1)
        bets = []
        match_title = FavoritScraper._get_match_title()
        if not match_title:
            return bets

        time.sleep(1)
        # selectors = []
        market_blocks = Page.driver.find_elements_by_class_name('markets--block')
        for mb in market_blocks:
            block_title = mb.find_element_by_class_name('markets--head').get_attribute('innerHTML')
            block_title_tail = mb.find_element_by_class_name('result--type--head')
            block_title += ' ' + block_title_tail.find_element_by_tag_name('span').get_attribute('innerHTML')
            labels = mb.find_elements_by_tag_name('label')
            for label in labels:
                bet_type = label.find_element_by_tag_name('span').get_attribute('title')
                bet_title = block_title + ' ' + bet_type
                button = label.find_element_by_tag_name('button')
                odds = button.get_attribute('innerHTML')
                bet = Bet(bet_title, odds)
                bets.append(bet)

        url = Page.driver.current_url
        match = Match(match_title, url, FavoritScraper._NAME, bets)
        return match

    @staticmethod
    def _get_match_title():
        """
        Scrapes match title from the current page

        :return: match title found on the page or None if nothing was found
        :rtype: str or None
        """
        try:
            init = Page.driver.find_element_by_class_name('two--name')
            teams = [el.get_attribute('innerHTML') for el in init.find_elements_by_tag_name('span')]
            match_title = MatchTitleCompiler.compile_match_title(*teams)
        except Exception as e:
            print(e)
            return None

        return match_title


if __name__ == '__main__':
    t = time.time()
    scraper = FavoritScraper()
    b = scraper.get_sport_bets(sport_name)
    pprint(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + sport_name + '\\favorit.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', pformat(b), file=f)

    print(time.time() - t)
