from pprint import pprint

from abstract_scraper import AbstractScraper
import time
from src.renderer.page import Page
from selenium.webdriver.common.keys import Keys


#  NAMING: match_title, bet_title, odds
class FavoritScraper(AbstractScraper):
    _BASE_URL = 'https://www.favorit.com.ua/en/bets/#'

    _MENU = {
        'csgo': ''
    }

    def get_bets(self, sport_type):
        """
        Scrapes betting data for a given sport type

        :param sport_type: sport type to scrape betting data for
        :type sport_type: str
        """
        bets = {}
        match_buttons = self.get_match_buttons(sport_type)
        for match_button in match_buttons:
            bets.update(FavoritScraper._get_bets(match_button))
            time.sleep(0.1)
        return bets

    @staticmethod
    def get_match_buttons(sport_type):
        """
        Scrape match buttons for a given sport type
        """
        page = Page(FavoritScraper._BASE_URL)

        if sport_type == 'csgo':
            headers = page.driver.find_elements_by_class_name('sport--name--head')
            for header in headers:
                if header.get_attribute('class') == 'sport--name--head sp_85':
                    cybersports = header
                    break
            time.sleep(0.25)
            page.driver.execute_script("arguments[0].click();", cybersports)
            time.sleep(0.25)
            drop_down_menu = cybersports.parent.find_element_by_class_name('slideInDown')
            checkboxes = drop_down_menu.find_elements_by_tag_name('b')
            # print(checkboxes)
            page.driver.execute_script("arguments[0].click();", checkboxes[1])
            time.sleep(0.25)

        main_table = page.driver.find_element_by_class_name('column--container')
        time.sleep(1)
        buttons = main_table.find_elements_by_class_name('event--more')
        # print(len(buttons))

        return buttons

    @staticmethod
    def _get_bets(match_button):
        """
        Scraps data such as match titles, bet titles and odds from the given match url

        :param match_button: any match button on the website
        :type match_button: button AHAHAHAHAHAHAHAH
        :return: bets dictionary in the following form:
        bets[match_title][bet_title] = odds
        :rtype: dict
        """
        Page.driver.execute_script("arguments[0].click();", match_button)
        time.sleep(0.1)
        bets = {}
        match_title = FavoritScraper._get_match_title()
        if not match_title:
            return bets
        bets[match_title] = {}
        time.sleep(1)
        marketBlocks = Page.driver.find_elements_by_class_name('markets--block')
        for mb in marketBlocks:
            block_title = mb.find_element_by_class_name('markets--head').get_attribute('innerHTML')
            block_title_tail = mb.find_element_by_class_name('result--type--head')
            block_title += ' ' + block_title_tail.find_element_by_tag_name('span').get_attribute('innerHTML')
            labels = mb.find_elements_by_tag_name('label')
            for label in labels:
                bet_type = label.find_element_by_tag_name('span').get_attribute('title')
                bet_title = block_title + ' ' + bet_type
                button = label.find_element_by_tag_name('button')

                odds = button.get_attribute('innerHTML')
                bets[match_title][bet_title] = odds

        return bets

    @staticmethod
    def _get_match_title():
        """
        Scrapes match title from the current page

        :return: match title found on the page or None if nothing was found
        :rtype: str or None
        """
        try:
            init = Page.driver.find_element_by_class_name('two--name')
            init = init.find_elements_by_tag_name('span')
            team1 = init[0].get_attribute('innerHTML').lower()
            team2 = init[1].get_attribute('innerHTML').lower()
            match_title = team1 + ' - ' + team2
        except Exception as e:
            print(e)
            return None
        return match_title


if __name__ == '__main__':
    t = time.time()

    scraper = FavoritScraper()
    b = scraper.get_bets('csgo')
    pprint(b)
    Page.driver.quit()

    print(time.time() - t)
