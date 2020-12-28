import os.path
import time

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from bet import Bet
from date_time import DateTime
from match import Match
from match_title import MatchTitle
from sport import Sport
from constants import SPORT_NAME
from src.scrapers.abstract_scraper import AbstractScraper


class OneXBetScraper(AbstractScraper):
    _NAME = 'one_x_bet'
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
    _SKIP_TITLES = ['Both Teams To Score Yes/No + Total', 'Result / Teams To Score', 'Draw + Total',
                    'Team 2, Result + Total', 'Team 1, Result + Total']

    def get_name(self) -> str:
        return self._NAME

    def get_matches_info_sport(self, sport_name):
        championships = self._get_championships(sport_name)
        championship_urls = OneXBetScraper.get_championship_urls(championships)
        print(len(championship_urls))

        match_elements = self._get_match_elements(championships)
        sport_matches = self._get_matches_info(match_elements, championship_urls)

        sport = Sport(sport_name, sport_matches)
        return sport

    def _get_matches_info(self, match_elements, championship_urls):
        matches = []
        base_len = len(OneXBetScraper._BASE_URL)

        for match_element in list(match_elements)[:]:
            try:
                url = match_element.get_attribute('href')[base_len:]
            except StaleElementReferenceException:
                print('Caught StaleElementReferenceException')
                continue

            if url in championship_urls or match_element.get_attribute('class') != 'link' or url.endswith(
                    '-Special-bets/'):
                continue

            match_title_text = match_element.find_element_by_class_name('gname').text
            match_title = MatchTitle.from_str(match_title_text)
            date_time_str = match_element.find_element_by_class_name('date').text
            try:
                date_time = DateTime.from_1xbet_str(date_time_str)
            except ValueError:
                print(url)
                continue
            match = Match(match_title, self._BASE_URL + url, date_time, self)
            matches.append(match)

        return matches

    def scrape_match_bets(self, match: Match):
        t = time.time()
        self.renderer.get(match.url)
        self._open_bets()
        soup = self.renderer.soup()

        bet_groups = soup.find_all(class_='bet_group')
        for bet_group in bet_groups:
            bet_title = bet_group.find(class_='bet-title').text
            if ' '.join(bet_title.split()) in OneXBetScraper._SKIP_TITLES:
                continue
            if '\nSlider' in bet_title:
                bet_title = bet_title[:-len('\nSlider')]

            bet_types = [el.text for el in bet_group.find_all(class_='bet_type')]
            odds = [el.text for el in bet_group.find_all(class_='koeff')]

            for i in range(len(bet_types)):
                bet = Bet(bet_title + '. ' + bet_types[i], odds[i], OneXBetScraper._NAME, match.url)
                match.bets.append(bet)
        print(self._NAME, time.time() - t)

    @staticmethod
    def get_championship_urls(championships):
        base_len = len(OneXBetScraper._BASE_URL)
        return [ch.get_attribute('href')[base_len:] for ch in championships]

    def _get_championships(self, sport_name):
        self.renderer.get(OneXBetScraper._BASE_URL)
        try:
            sport = self.renderer.find_element_by_css_selector('a[href^="' + OneXBetScraper._MENU[sport_name] + '"]')
        except NoSuchElementException:
            print('Caught NoSuchElementException("a[href^="line/Esports/"]), retrying...')
            return self._get_championships(sport_name)
        self.renderer.click(sport)
        time.sleep(2)

        try:
            menu = self.renderer.find_element_by_class_name('liga_menu')
        except NoSuchElementException:
            print('Caught NoSuchElementException("liga-menu"), retrying...')
            return self._get_championships(sport_name)

        pattern = OneXBetScraper._SPORT_NAMES[sport_name]
        selector = 'a[href*="' + pattern + '"]'

        championships = {el for el in menu.find_elements_by_css_selector(selector) if el.get_attribute('href').count(
            '/') == 7}

        return championships

    def _get_match_elements(self, championships):
        matches = set()
        menu = self.renderer.find_element_by_class_name('liga_menu')
        championship_urls = OneXBetScraper.get_championship_urls(championships)

        print('Opening championships...')
        self._open_championships(championships)

        print('Retrieving matches...')
        event_menus = menu.find_elements_by_class_name('event_menu')
        print('Event menus count: ' + str(len(event_menus)))
        for championship_url in championship_urls:
            css_link_prefix_match = 'a[href^="' + championship_url + '"]'
            try:
                matches.update(el for el in menu.find_elements_by_css_selector(css_link_prefix_match))
            except NoSuchElementException:
                pass

        return matches

    def _open_championships(self, championships):
        for championship in championships:
            if championship.find_element_by_xpath('..').get_attribute('class') != 'open':
                self.renderer.click(championship)

    def _open_bets(self):
        elements = self.renderer.find_elements_by_class_name('bet-title')

        for element in elements:
            if element.get_attribute('class') == 'bet-title bet-title_justify min':
                self.renderer.click(element)


if __name__ == '__main__':
    t = time.time()
    scraper = OneXBetScraper()
    sport = scraper.get_matches_info_sport(SPORT_NAME)
    # for match in sport:
    #     scraper.scrape_match_bets(match)
    print(sport)

    scraper.renderer.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + SPORT_NAME + '\\' + scraper.get_name()
    sport.serialize(path)
    with open(path + '.py', 'w', encoding='utf-8') as f:
        print('sport =', sport, file=f)
    print(time.time() - t)
