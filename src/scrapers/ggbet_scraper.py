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
from selenium.webdriver.common.keys import Keys


class GGBetScraper(AbstractScraper):
    _NAME = 'ggbet'
    _BASE_URL = 'https://gg.bet/en/'
    _TAIL_URL = {
        'csgo': 'betting',
        'dota': 'betting',
        'football': 'betting-sports'
    }
    _MENU = {
        'csgo': 'Counter-Strike',
        'dota': 'Dota 2',
        'football': 'Soccer'
    }

    def get_sport_bets(self, sport_name):
        """
        Scrapes betting data for a given sport type

        :param sport_name: sport type to scrape betting data for
        :type sport_name: str
        """
        sport_bets = []
        match_urls = self.get_match_urls(sport_name)
        # match_urls = match_urls[:20]
        for url in match_urls:
            match_bets = GGBetScraper._get_bets(url)
            if match_bets:
                sport_bets.append(match_bets)
        sport = Sport(sport_name, sport_bets)
        return sport

    @staticmethod
    def get_match_urls(sport_name):
        """
        Scrape match urls for a given sport type
        """
        urls = []
        page = Page(GGBetScraper._BASE_URL + GGBetScraper._TAIL_URL[sport_name])
        time.sleep(1)
        sport_types = Page.driver.find_elements_by_class_name('__app-CategorizerRowHeader-container')
        sport_type_icon = sport_types[0]
        for sport_type in sport_types:
            if sport_type.find_element_by_class_name('CategorizerRowHeader__label___LQD65').get_attribute('title') == GGBetScraper._MENU[sport_name]:
                sport_type_icon = sport_type
        page.click(sport_type_icon)
        time.sleep(1)
        tournament_block = Page.driver.find_element_by_class_name('categorizerRow__submenu___tyhYn')
        tournaments = tournament_block.find_elements_by_class_name('categorizerCheckRow__row___EW7wX')
        for tournament in tournaments:
            number_of_matches = tournament.find_element_by_class_name('categorizerCheckRow__counter___3rFMF')
            number_of_matches = int(number_of_matches.text)
            page.click(tournament)
            time.sleep(1)
            if number_of_matches > 20:
                GGBetScraper.scroll_down()
            middle_table = page.driver.find_element_by_class_name('ScrollToTop__container___37xDi')
            links = middle_table.find_elements_by_class_name('marketsCount__markets-count___v4kPh')
            urls += [link.get_attribute('href') for link in links]
            page.click(tournament)
            time.sleep(1)
        return urls

    @staticmethod
    def scroll_down():
        last_height = Page.driver.execute_script("return document.body.scrollHeight")
        while True:
            html = Page.driver.find_element_by_tag_name('html')
            for _ in (1, 3):
                html.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.25)
            for _ in (1, 3):
                html.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.25)
            for _ in (1, 3):
                html.send_keys(Keys.PAGE_UP)
                time.sleep(0.25)
            for _ in (1, 3):
                html.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.25)

            new_height = Page.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

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
        page = Page(match_url)
        time.sleep(2)
        bets = []
        match_title = GGBetScraper._get_match_title()
        if not match_title:
            return bets

        # live_buttons = page.driver.find_elements_by_class_name('__app-LiveIcon-container')
        # if len(live_buttons) > 1:
        #     # is live
        #     return bets

        market_tables = page.driver.find_elements_by_class_name('marketTable__table___dvHTz')
        for mt in market_tables:
            table_title = mt.find_element_by_class_name('marketTable__header___mSHxT').get_attribute('title')
            buttons = mt.find_elements_by_tag_name('button')
            for button in buttons:
                try:
                    bet = button.get_attribute('title')
                    if bet != 'Deactivated':
                        pos = bet.find(': ')
                        bet_type = bet[:pos]
                        odd = bet[pos + 2:]
                        bet_title = table_title + ' ' + bet_type
                        bet = Bet(bet_title, odd)
                        bets.append(bet)
                except Exception as e:
                    print('ggbet error in buttons')
        match = Match(match_title, match_url, GGBetScraper._NAME, bets)
        return match

    @staticmethod
    def _get_match_title():
        """
        Scrapes match title from the current page

        :return: match title found on the page or None if nothing was found
        :rtype: str or None
        """
        try:
            teams = [el.get_attribute('innerHTML') for el in Page.driver.find_elements_by_class_name(
                '__app-PromoMatchBody-competitor-name')]
            match_title = MatchTitleCompiler.compile_match_title(*teams[:2])
        except Exception as e:
            print(e)
            return None

        return match_title


if __name__ == '__main__':
    t = time.time()
    scraper = GGBetScraper()
    b = scraper.get_sport_bets(sport_name)
    pprint(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    print(my_path)
    path = my_path + '\\sample_data\\' + sport_name + '\\ggbet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', pformat(b), file=f)
    print(time.time() - t)
