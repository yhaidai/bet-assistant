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
    _ICONS = {
        'football': 'Soccer',
        'csgo': 'Cybersports',
        'dota': 'Cybersports'
        }
    _SUBMENU = {
        'football': None,
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
        subsections = self.get_subsections(sport_name)
        for subsection in subsections:
            match_buttons = self.get_match_buttons(subsection)
            for match_button in match_buttons:
                match_bets = FavoritScraper._get_bets(match_button)
                if match_bets:
                    sport_bets.append(match_bets)
            Page.click(subsection)
            time.sleep(1)
        sport = Sport(sport_name, sport_bets)
        return sport

    @staticmethod
    def get_match_buttons(subsection):
        Page.click(subsection)
        time.sleep(1)
        main_table = Page.driver.find_element_by_class_name('column--container')
        time.sleep(1)
        buttons = main_table.find_elements_by_class_name('event--more')
        return buttons

    @staticmethod
    def get_subsections(sport_name):
        """
        Scrape match buttons for a given sport type
        """
        page = Page(FavoritScraper._BASE_URL)
        sports_list = Page.driver.find_elements_by_class_name('sprt')
        icon = sports_list[0].find_element_by_class_name('sport--name--head')

        for sport in sports_list:
            if sport.find_element_by_class_name('ttt').get_attribute('innerHTML') == FavoritScraper._ICONS[sport_name]:
                print(FavoritScraper._ICONS[sport_name])
                icon = sport.find_element_by_class_name('sport--name--head')
                break

        time.sleep(0.25)
        page.click(icon)
        time.sleep(0.25)
        drop_down_menu = icon.parent.find_element_by_class_name('slideInDown')
        checkboxes = drop_down_menu.find_elements_by_tag_name('b')
        titles = drop_down_menu.find_elements_by_class_name('ttt')

        if FavoritScraper._SUBMENU[sport_name]:
            for i in range(len(checkboxes)):
                if titles[i].get_attribute('innerHTML') == FavoritScraper._SUBMENU[sport_name]:
                    return [checkboxes[i]]
                    # page.click(checkboxes[i])
        time.sleep(0.25)

        return checkboxes

    @staticmethod
    def _get_bets(match_button):
        Page.click(match_button)
        time.sleep(0.1)
        bets = []
        url = Page.driver.current_url
        match_title = FavoritScraper._get_match_title()
        if not match_title:
            return bets

        time.sleep(0.25)
        # selectors = []
        market_blocks = Page.driver.find_elements_by_class_name('markets--block')
        for mb in market_blocks:
            block_title = mb.find_element_by_class_name('markets--head').get_attribute('innerHTML')
            block_title_tail = mb.find_element_by_class_name('result--type--head')
            block_title += ' ' + block_title_tail.find_element_by_tag_name('span').get_attribute('innerHTML')
            labels = mb.find_elements_by_tag_name('label')
            if mb.find_elements_by_class_name('mtype--7'):
                continue
            # print(block_title)
            for label in labels:
                if label.get_attribute('class') == 'outcome--empty':
                    continue
                bet_type = label.find_element_by_tag_name('span').get_attribute('title')
                # print(bet_type)
                bet_title = block_title + ' ' + bet_type
                button = label.find_element_by_tag_name('button')
                odds = button.get_attribute('innerHTML')
                bet = Bet(bet_title, odds, FavoritScraper._NAME, url)
                bets.append(bet)

        match = Match(match_title, bets)
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
