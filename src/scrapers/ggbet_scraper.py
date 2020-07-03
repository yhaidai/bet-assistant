from pprint import pprint, pformat
import os.path
from abstract_scraper import AbstractScraper
import time
from src.renderer.page import Page
from selenium.webdriver.common.keys import Keys


class GGBetScraper(AbstractScraper):
    _BASE_URL = 'https://gg.bet/en/betting/'

    _MENU = {
        'csgo': '//*[@id="betting__container"]/div/div/div[1]/div/div/div[5]/div[1]/div[2]'
    }

    def get_bets(self, sport_type):
        """
        Scrapes betting data for a given sport type

        :param sport_type: sport type to scrape betting data for
        :type sport_type: str
        """
        bets = {}
        match_urls = self.get_match_urls(sport_type)
        for url in match_urls:
<<<<<<< HEAD
            bets.update(GGBetScraper._get_bets(url))
            time.sleep(0.1)
=======
            match_bets = GGBetScraper._get_bets(url)
            for match_title in match_bets:
                match_bets[match_title][self.match_url_key] = url
            bets.update(match_bets)
            # time.sleep(0.5)
>>>>>>> e582648b26037ee6c83b53a3fc50541140242e27
        return bets

    @staticmethod
    def get_match_urls(sport_type):
        """
        Scrape match urls for a given sport type
        """
        page = Page(GGBetScraper._BASE_URL)
        time.sleep(1)
        sport_type_icon = page.driver.find_element_by_xpath(GGBetScraper._MENU[sport_type])
        time.sleep(1)
        page.click(sport_type_icon)

        GGBetScraper.scroll_down()

        links = page.driver.find_elements_by_class_name('marketsCount__markets-count___v4kPh')
        urls = [link.get_attribute('href') for link in links]
        return urls

    @staticmethod
    def scroll_down():
        last_height = Page.driver.execute_script("return document.body.scrollHeight")
        while True:
            html = Page.driver.find_element_by_tag_name('html')
            for _ in (1, 5):
                html.send_keys(Keys.PAGE_DOWN)
            for _ in (1, 3):
                html.send_keys(Keys.PAGE_UP)
            for _ in (1, 3):
                html.send_keys(Keys.PAGE_DOWN)

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
        bets = {}
        match_title = GGBetScraper._get_match_title()
        if not match_title:
            return bets
        bets[match_title] = {}

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
                        odds = bet[pos + 2:]
                        bet_title = table_title + ' ' + bet_type
                        bets[match_title][bet_title] = odds
                except Exception as e:
                    print('ggbet error in buttons')

        return bets

    @staticmethod
    def _get_match_title():
        """
        Scrapes match title from the current page

        :return: match title found on the page or None if nothing was found
        :rtype: str or None
        """
        try:
            init = Page.driver.find_elements_by_class_name('__app-PromoMatchBody-competitor-name')
            team1 = init[0].get_attribute('innerHTML').lower()
            team2 = init[1].get_attribute('innerHTML').lower()
            match_title = team1 + ' - ' + team2
        except Exception as e:
            print(e)
            return None
        return match_title


if __name__ == '__main__':
    t = time.time()
    scraper = GGBetScraper()
    b = scraper.get_bets('csgo')
    pprint(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    print(my_path)
    path = my_path + '\\sample_data\\ggbet.py'
    with open(path, 'w', encoding = 'utf-8') as f:
        print('bets = ', pformat(b), file = f)
    print(time.time() - t)

