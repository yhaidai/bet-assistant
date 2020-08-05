import os.path

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

from bet import Bet
from date_time import DateTime
from match import Match
from match_title import MatchTitle
from sport import Sport
from abstract_scraper import AbstractScraper
import time

from constants import sport_name
from src.renderer.page import Page
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


wait = WebDriverWait(Page.driver, 20)
LIVE = False
tournament_names = None
country_names = None


class GGBetScraper(AbstractScraper):
    _NAME = 'ggbet'
    _BASE_URL = 'https://gg.bet/en/'
    _TAIL_URL = {
        'csgo': 'betting',
        'dota': 'betting',
        'lol': 'betting',
        'football': 'betting-sports'
    }
    _MENU = {
        'csgo': 'Counter-Strike',
        'dota': 'Dota 2',
        'football': 'Soccer',
        'lol': 'League of Legends'
    }

    def get_sport_bets(self, sport_name):
        """
        Scrapes betting data for a given sport type

        :param sport_name: sport type to scrape betting data for
        :type sport_name: str
        """
        sport_bets = []
        match_urls = self.get_match_urls(self, sport_name)
        # match_urls = match_urls[:20]
        for url in match_urls:
            print('  match', match_urls.index(url) + 1, '/', len(match_urls))
            match_bets = GGBetScraper._get_bets_from_url(url)
            if match_bets:
                sport_bets.append(match_bets)
            break
        sport = Sport(sport_name, sport_bets)
        return sport

    @staticmethod
    def get_match_urls(self, sport_name):
        """
        Scrape match urls for a given sport type
        """
        urls = []
        tournaments = self.get_tournaments(sport_name)
        for tournament in tournaments:
            number_of_matches = tournament.find_element_by_class_name('categorizerCheckRow__counter___3rFMF')
            number_of_matches = int(number_of_matches.text)
            Page.click(tournament)
            time.sleep(1)
            if number_of_matches > 20:
                GGBetScraper.scroll_down()
            middle_table = Page.driver.find_element_by_class_name('ScrollToTop__container___37xDi')
            links = middle_table.find_elements_by_class_name('marketsCount__markets-count___v4kPh')
            urls += [link.get_attribute('href') for link in links]
            Page.click(tournament)
            time.sleep(1)
        return urls

    @staticmethod
    def get_tournaments(sport_name):
        print(sport_name)
        url = GGBetScraper._BASE_URL + GGBetScraper._TAIL_URL[sport_name]
        # if LIVE:
        #     url += '/live'
        Page(url)
        time.sleep(2)
        try:
            sport_types = wait.until(EC.presence_of_all_elements_located
                                     ((By.CLASS_NAME, '__app-CategorizerRowHeader-container')))
        except TimeoutException:
            return GGBetScraper.get_tournaments(sport_name)
        # sport_types = Page.driver.find_elements_by_class_name('__app-CategorizerRowHeader-container')
        sport_type_icon = sport_types[0]
        try:
            for sport_type in sport_types:
                if sport_type.find_element_by_class_name('CategorizerRowHeader__label___LQD65').get_attribute('title') == \
                        GGBetScraper._MENU[sport_name]:
                    sport_type_icon = sport_type
            time.sleep(2)
            Page.click(sport_type_icon)
        except StaleElementReferenceException:
            print('caught StaleElementReferenceException, retrying...')
            return GGBetScraper.get_tournaments(sport_name)
        # if LIVE:
        #     number_of_matches = sport_type_icon.find_element_by_class_name('CategorizerRowHeader__counter___1xRCu')
        #     number_of_matches = int(number_of_matches.text)
        #     time.sleep(1)
        #     if number_of_matches > 20:
        #         GGBetScraper.scroll_down()
        #     return [1]
        time.sleep(2)
        try:
            tournament_block = wait.until(EC.presence_of_element_located
                                      ((By.CLASS_NAME, 'categorizerRow__submenu___tyhYn')))
        except TimeoutException:
            return GGBetScraper.get_tournaments(sport_name)
        # tournament_block = Page.driver.find_element_by_class_name('categorizerRow__submenu___tyhYn') #wait
        tournaments = tournament_block.find_elements_by_class_name('categorizerCheckRow__row___EW7wX')
        if sport_name == 'football':
            if tournament_names:
                _tournaments = []
                for tournament_name in tournament_names:
                    _tournaments += [t for t in tournaments if tournament_name in t.text.lower()]
                tournaments = _tournaments
            if country_names:
                for tournament in list(tournaments):
                    b = False
                    for country_name in country_names:
                        if country_name in tournament.text.lower():
                            b = True
                            break
                    if not b:
                        tournaments.remove(tournament)
        print('scraping', len(tournaments), 'tournaments')
        return tournaments

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
    def _get_bets_from_url(match_url):
        """
        Scraps data such as match titles, bet titles and odds from the given match url

        :param match_url: any match url on the website
        :type match_url: str
        :return: bets dictionary in the following form:
        bets[match_title][bet_title] = odds
        :rtype: dict
        """
        Page(match_url)
        time.sleep(2)
        bets = []
        main_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Match__container___fpI_d')))
        # main_table = Page.driver.find_element_by_class_name('Match__container___fpI_d')
        teams = [el.text for el in main_table.find_elements_by_class_name(
            '__app-PromoMatchBody-competitor-name')]
        # print(teams)
        try:
            date = main_table.find_element_by_class_name('dateTime__date___2QS99').text.lower()
        except Exception:
            date = ''
        match = Match(MatchTitle(teams), match_url, date)

        GGBetScraper._parse_marketblocks(bets, match_url)

        match.bets = bets
        return match

    @staticmethod
    def _parse_marketblocks(bets, match_url):
        market_tables = wait.until(EC.presence_of_all_elements_located
                   ((By.CLASS_NAME, 'marketTable__table___dvHTz')))
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
                        bet = Bet(bet_title, odds, GGBetScraper._NAME, match_url)
                        bets.append(bet)
                except Exception as e:
                    print('ggbet error in buttons')

    def get_matches_info_sport(self, sport_name):
        matches = []
        subsections = self.get_tournaments(sport_name)
        for subsection in subsections:
            # if not LIVE:
            Page.click(subsection)
                # print(' ', subsections.index(subsection) + 1)
            time.sleep(2)
            events = Page.driver.find_elements_by_class_name('sportEventRow__body___3Ywcg')
            time.sleep(2)
            for event in events:
                try:
                    event.find_element_by_class_name('matchDateTime__isLive___8f4IP')
                    continue  # match is live
                except NoSuchElementException:
                    pass
                except StaleElementReferenceException:
                    continue
                date_text = event.find_element_by_class_name('matchDateTime__date___2Hw-c').text
                teams_webel = event.find_elements_by_class_name('__app-LogoTitle-wrapper')
                teams = [el.text for el in teams_webel]
                url = teams_webel[0].find_element_by_tag_name('a').get_attribute('href')
                date = DateTime.from_ggbet_str(date_text)
                matches.append(Match(MatchTitle(teams), url, date, self))
            # if not LIVE:
            Page.click(subsection)
        print(len(matches))
        return Sport(sport_name, matches)

    @staticmethod
    def scrape_match_bets(match):
        Page(match.url)
        # if not LIVE:
        #     if not match.date:
        #         print('this match is probably live')
        #         return None
        time.sleep(2)
        GGBetScraper._parse_marketblocks(match.bets, match.url)
        return match

    @staticmethod
    def _get_bets_from_live_match_with_basic_data(match):
        Page(match.url)
        while True:
            bets = []
            GGBetScraper._parse_marketblocks(bets, match.url)
            match.bets = bets
            # print_variable('live', GGBetScraper._NAME, 'match = ', match)
            time.sleep(0.5)

    def _get_bets_one_by_one(self, sport_name):
        sport_bets = []
        matches = self.get_matches_info_sport(sport_name).matches
        for match in matches:

            print('match', matches.index(match) + 1, '/', len(matches))
            print(match.date)
            match_bets = GGBetScraper.scrape_match_bets(match)
            if match_bets:
                sport_bets.append(match_bets)
            break
        sport = Sport(sport_name, sport_bets)
        return sport


if __name__ == '__main__':
    t = time.time()
    scraper = GGBetScraper()
    sport = scraper.get_matches_info_sport(sport_name)
    print(sport)
    for match in sport:
        scraper.scrape_match_bets(match)
    # sport = scraper._get_urls_and_titles(sport_name)
    print(sport)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    print(my_path)
    path = my_path + '\\sample_data\\' + sport_name + '\\ggbet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', sport, file=f)
    print(time.time() - t)
