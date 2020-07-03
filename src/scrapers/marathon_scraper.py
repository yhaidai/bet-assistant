from pprint import pprint, pformat
import os.path
from abstract_scraper import AbstractScraper
import time
from src.renderer.page import Page
from selenium.webdriver.common.keys import Keys


#  NAMING: match_title, bet_title, odds
class MarathonScraper(AbstractScraper):
    _BASE_URL = 'https://www.marathonbet.com/en/'

    _MENU = {
        'csgo': 'CS:GO.'
    }

    def get_bets(self, sport_type):
        """
        Scrapes betting data for a given sport type

        :param sport_type: sport type to scrape betting data for
        :type sport_type: str
        """
        bets = {}
        matches = self.get_matches(sport_type)
        for match in matches:
            bets.update(MarathonScraper._get_bets(match))
            time.sleep(0.1)
        return bets

    @staticmethod
    def get_matches(sport_type):
        """
        Scrape match elements for a given sport type
        """
        page = Page(MarathonScraper._BASE_URL)

        matches = []

        if sport_type == 'csgo':
            icon = page.driver.find_element_by_class_name('icon-sport-e-sports')
            page.driver.execute_script("arguments[0].click();", icon)
            time.sleep(0.2)
            tournaments = page.driver.find_elements_by_class_name('category-container')
            for tournament in tournaments:
                sport_type = tournament.find_element_by_class_name('nowrap')
                if sport_type.get_attribute('innerHTML') != 'CS:GO.':
                    break
                matches += tournament.find_elements_by_class_name('bg')

        return matches

    @staticmethod
    def _get_bets(match):
        """
        Scraps data such as match titles, bet titles and odds from the given match url

        :param match: any match on the website
        :type match: match AHAHAHAHAHAHAHAH
        :return: bets dictionary in the following form:
        bets[match_title][bet_title] = odds
        :rtype: dict
        """

        bets = {}
        teams = match.find_elements_by_tag_name('span')
        team1 = teams[0].get_attribute('innerHTML').lower()
        team2 = teams[1].get_attribute('innerHTML').lower()
        match_title = team1 + ' - ' + team2
        if not match_title:
            return bets
        bets[match_title] = {}
        main_odds = match.find_elements_by_class_name('selection-link')
        bets[match_title][team1 + ' will win'] = main_odds[0].get_attribute('innerHTML')
        bets[match_title][team2 + ' will win'] = main_odds[1].get_attribute('innerHTML')
        url = Page.driver.current_url
        # xpaths = []
        try:
            match_button = match.find_element_by_class_name('event-more-view')
            Page.driver.execute_script("arguments[0].click();", match_button)
            time.sleep(0.5)
        except Exception:
            print('no more-view button', match_title)
            return bets

        shortcuts = match.find_element_by_class_name('details-description')
        all_markets_button = shortcuts.find_element_by_tag_name('td')
        Page.driver.execute_script("arguments[0].click();", all_markets_button)
        time.sleep(0.5)
        marketBlocks = Page.driver.find_elements_by_class_name('market-inline-block-table-wrapper')
        for mb in marketBlocks:
            block_title = mb.find_element_by_class_name('name-field').get_attribute('innerHTML')
            table = mb.find_element_by_class_name('td-border')
            results_left = mb.find_elements_by_class_name('result-left')

            if results_left:
                odds = table.find_elements_by_class_name('result-right')
                for i in range(len(results_left)):
                    result_left = results_left[i].get_attribute('innerHTML')
                    odd = odds[i].find_element_by_tag_name('span').get_attribute('innerHTML')
                    bet_title = block_title + ' ' + result_left
                    bets[match_title][bet_title] = odd
            else:
                rows = table.find_elements_by_tag_name('tr')
                for row in rows:
                    tags_raw = row.find_elements_by_tag_name('th')
                    if tags_raw:
                        for i in range(len(tags_raw)):
                            try:
                                tags_raw[i] = tags_raw[i].find_element_by_tag_name('div')
                            except Exception as e:
                                break
                        tags = [tag_raw.get_attribute('innerHTML') for tag_raw in tags_raw]
                    else:
                        bet_types = row.find_elements_by_class_name('coeff-value')
                        odds = row.find_elements_by_class_name('selection-link')
                        for i in range(len(odds)):
                            bet_type = ''
                            if bet_types:
                                bet_type = bet_types[i].get_attribute('innerHTML')
                            odd = odds[i].get_attribute('innerHTML')
                            bet_title = block_title + ' ' + tags[i] + ' ' + bet_type
                            bets[match_title][bet_title] = odd
        Page.driver.execute_script("arguments[0].click();", match_button)
        time.sleep(0.2)
        return bets

    @staticmethod
    def _get_match_title(match):
        """
        Scrapes match title from the current page

        :return: match title found on the page or None if nothing was found
        :rtype: str or None
        """
        try:
            teams = match.find_elements_by_tag_name('span')
            team1 = teams[0].get_attribute('innerHTML').lower()
            team2 = teams[1].get_attribute('innerHTML').lower()
            match_title = team1 + ' - ' + team2
        except Exception as e:
            print(e)
            return None
        return match_title


if __name__ == '__main__':
    t = time.time()

    scraper = MarathonScraper()
    b = scraper.get_bets('csgo')
    pprint(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\marathon.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('bets = ', pformat(b), file=f)
    print(time.time() - t)
