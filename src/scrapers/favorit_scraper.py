import os.path
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from bet import Bet
from date_time import DateTime
from match import Match
from match_title import MatchTitle
from sport import Sport
from abstract_scraper import AbstractScraper
from constants import sport_name
from match_title_compiler import MatchTitleCompiler
from src.renderer.page import Page


tournament_names = None
country_names = None


class FavoritScraper(AbstractScraper):
    _NAME = 'favorit'
    _BASE_URL = 'https://www.favorit.com.ua/en/bets/#'
    _LIVE_URL = 'https://www.favorit.com.ua/en/live/'
    _ICONS = {
        'football': 'Soccer',
        'csgo': 'Cybersports',
        'dota': 'Cybersports',
        'lol': 'Cybersports',
    }
    _SUBMENU = {
        'football': None,
        'csgo': 'Counter-Strike: Global Offensive',
        'dota': 'Dota 2',
        'lol': 'League of Legends'
    }
    _SKIP_TITLES = ['1X2 and Total Goals', '1X2 and Both teams to Score',
                    'Both Teams To Score and Total Goals', 'Correct Score',
                    'Goal method of first goal', '(3way)', 'Winning Margin',
                    'not to lose and Total', 'Goal Range', 'Goal method of first goal',
                    'HT/FT', 'HT or FT and Total Goals', 'Both Teams To Score and Total Goals']

    wait = WebDriverWait(Page.driver, 10)

    def get_sport_bets(self, sport_name):
        """
        Scrapes betting data for a given sport type

        :param sport_name: sport type to scrape betting data for
        :type sport_name: str
        """
        sport_bets = []
        subsections = self.get_subsections(sport_name)

        # subsections = [subsections[6]]

        for subsection in subsections:

            print('subsection', subsections.index(subsection) + 1, '/', len(subsections))

            tournaments = self.get_subsection_tournaments(subsection)
            for tournament in tournaments:

                print(' ' * 1, 'tournament', tournaments.index(tournament) + 1, '/', len(tournaments))

                events = self.get_events_from_tournament(tournament)
                for event in events:

                    print(' ' * 4, 'match', events.index(event) + 1, '/', len(events))

                    match_bets = FavoritScraper._get_bets(event)
                    if match_bets:
                        sport_bets.append(match_bets)
                    break
                break
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
    def get_match_buttons_from_tournament(tournament):
        buttons = tournament.find_elements_by_class_name('event--more')
        return buttons

    @staticmethod
    def get_events_from_tournament(tournament):
        events = tournament.find_elements_by_class_name('event--head-block')
        return events

    @staticmethod
    def get_events(subsection):
        Page.click(subsection)
        time.sleep(1)
        main_table = Page.driver.find_element_by_class_name('column--container')
        time.sleep(1)
        events = main_table.find_elements_by_class_name('event--head-block')
        return events

    @staticmethod
    def get_subsection_tournaments(subsection):
        Page.click(subsection)
        time.sleep(2)
        tournaments = Page.driver.find_element_by_class_name('sport--list').find_elements_by_class_name(
            'category--block')
        if FavoritScraper._ICONS[sport_name] != 'Cybersports':
            if tournament_names:
                for t in list(tournaments):
                    for name in tournament_names:
                        if name not in t.find_element_by_class_name('category--name').text.lower():
                            tournaments.remove(t)
        return tournaments

    @staticmethod
    def get_subsections(sport_name):
        """
        Scrape match buttons for a given sport type
        """
        Page('https://www.google.com/')
        Page(FavoritScraper._BASE_URL)
        sports_list = Page.driver.find_elements_by_class_name('sprt')
        icon = sports_list[0].find_element_by_class_name('sport--name--head')

        for sport in sports_list:
            if sport.find_element_by_class_name('ttt').text == FavoritScraper._ICONS[sport_name]:
                icon = sport.find_element_by_class_name('sport--name--head')
                break

        time.sleep(0.25)
        Page.click(icon)
        time.sleep(0.25)

        drop_down_menu = icon.parent.find_element_by_class_name('slideInDown')
        checkboxes = drop_down_menu.find_elements_by_tag_name('b')
        titles = drop_down_menu.find_elements_by_class_name('ttt')

        if FavoritScraper._SUBMENU[sport_name]:
            for i in range(len(checkboxes)):
                if titles[i].text == FavoritScraper._SUBMENU[sport_name]:
                    return [checkboxes[i]]

        if FavoritScraper._ICONS[sport_name] != 'Cybersports':
            if country_names:
                for checkbox in list(checkboxes):
                    b = False
                    for country_name in country_names:
                        if country_name in checkbox.find_element_by_xpath('..').text.lower():
                            b = True
                            break
                    if not b:
                        checkboxes.remove(checkbox)
        print('scraping', len(checkboxes), 'subsections')
        return checkboxes

    @staticmethod
    def _get_bets(event):
        bets = []
        # time.sleep(0.1)
        match = FavoritScraper._get_match_basic_data(event)
        match_button = event.find_element_by_class_name('event--more')
        Page.click(match_button)
        time.sleep(0.1)

        if int(match_button.text) > 3:  # otherwise no need to click it
            time.sleep(1)
            try:
                element = FavoritScraper.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'slick-block')))
                Page.click(element)
            except Exception:
                pass

        time.sleep(0.5)
        FavoritScraper._parse_marketblocks(bets, match.url)

        match.bets = bets
        return match

    @staticmethod
    def _parse_marketblocks(bets, url):
        market_blocks = FavoritScraper.wait.until(EC.presence_of_all_elements_located
                                   ((By.CLASS_NAME, 'markets--block')))
        for mb in market_blocks:
            block_title_head = mb.find_element_by_class_name('markets--head').get_attribute('innerHTML')

            b = True
            for s in FavoritScraper._SKIP_TITLES:
                if s in block_title_head:
                    b = False
                    break
            if not b:
                # print(block_title_head)
                continue
            # print(block_title_head)
            sub_block_titles = mb.find_elements_by_class_name('result--type--head')
            sub_blocks = mb.find_elements_by_class_name('outcome--list')
            for sub_block in sub_blocks:
                block_title_tail = ' ' + sub_block_titles[sub_blocks.index(sub_block)].find_element_by_tag_name(
                    'span').get_attribute('innerHTML')
                block_title = block_title_head + block_title_tail
                block = sub_block

                if mb.find_elements_by_class_name('mtype--7'):
                    break
                else:
                    labels = block.find_elements_by_tag_name('label')
                    for label in labels:
                        if label.get_attribute('class') == 'outcome--empty':
                            continue
                        bet_type = label.find_element_by_tag_name('span').get_attribute('title')
                        bet_title = block_title + ' ' + bet_type
                        button = label.find_element_by_tag_name('button')
                        odds = button.text
                        bet = Bet(bet_title, odds, FavoritScraper._NAME, url)
                        bets.append(bet)

    @staticmethod
    def _parse_live_marketblocks(bets, url):
        market_blocks = Page.driver.find_elements_by_class_name('markets--block')
        for mb in market_blocks:
            try:
                block_title_head = mb.find_element_by_class_name('markets--head').get_attribute('innerHTML')

                b = True
                for s in FavoritScraper._SKIP_TITLES:
                    if s in block_title_head:
                        b = False
                        break
                if not b:
                    # print(block_title_head)
                    continue
                print(market_blocks.index(mb))
                sub_block_titles = mb.find_elements_by_class_name('result--type--head')
                sub_blocks = mb.find_elements_by_class_name('outcome--list')
                for sub_block in sub_blocks:
                    block_title_tail = ' ' + sub_block_titles[sub_blocks.index(sub_block)].find_element_by_tag_name(
                        'span').get_attribute('innerHTML')
                    block_title = block_title_head + block_title_tail
                    block = sub_block

                    if mb.find_elements_by_class_name('mtype--7'):
                        break
                    else:
                        labels = block.find_elements_by_tag_name('label')
                        for label in labels:
                            if label.get_attribute('class') == 'outcome--empty':
                                continue
                            bet_type = label.find_element_by_tag_name('span').get_attribute('title')
                            bet_title = block_title + ' ' + bet_type
                            button = label.find_element_by_tag_name('button')
                            odds = button.text
                            bet = Bet(bet_title, odds, FavoritScraper._NAME, url)
                            bets.append(bet)
            except Exception:
                pass
        return bets

    @staticmethod
    def _get_bets_from_url(match_url):
        Page(match_url)
        bets = []
        basic_info = FavoritScraper.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sticky-inner-wrapper')))
        # basic_info = Page.driver.find_element_by_class_name('sticky-inner-wrapper')

        date = basic_info.find_element_by_class_name('event--date--1').text.lower()
        date = FavoritScraper._format_date(date)
        teams = [el.text for el in
                 basic_info.find_element_by_class_name('event--name').find_elements_by_tag_name('span')]
        match = Match(MatchTitle(teams), match_url, date)
        element = FavoritScraper.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'slick-block')))
        element = FavoritScraper.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'slick-block')))
        try:
            Page.click(element)
        except Exception:
            print('ne mogu nazhat na all')

        time.sleep(0.5)
        FavoritScraper._parse_marketblocks(bets, match_url)

        match.bets = bets
        return match

    @staticmethod
    def scrape_match_bets(match):
        Page(match.url)

        wait = WebDriverWait(Page.driver, 10)
        try:
            element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'slick-block')))
            Page.click(element)
        except TimeoutException:
            pass

        time.sleep(0.5)
        FavoritScraper._parse_marketblocks(match.bets, match.url)

        return match

    @staticmethod
    def _get_bets_from_live_match_with_basic_data(match):
        Page(match.url)
        time.sleep(0.5)
        while True:
            bets = []
            FavoritScraper._parse_live_marketblocks(bets, match.url)
            match.bets = bets
            # print_variable('live', FavoritScraper._NAME, 'match = ', match)
            time.sleep(0.5)

    def get_matches_info_sport(self, sport_name):
        matches = []
        subsections = self.get_subsections(sport_name)
        for subsection in subsections:
            tournaments = self.get_subsection_tournaments(subsection)
            time.sleep(1)
            print(' ', subsections.index(subsection) + 1)
            for tournament in tournaments:
                events = tournament.find_elements_by_class_name('event--head-block')
                for event in events:
                    matches.append(self._get_match_basic_data(event))
                    # break
            Page.click(subsection)
            time.sleep(1)

        return Sport(sport_name, matches)

    def _get_match_basic_data(self, event):
        date = event.find_element_by_class_name('event--date').text
        time = event.find_element_by_class_name('event--time').text
        date_time_str = date + time
        date_time = DateTime.from_favorit_str(date_time_str)
        name = event.find_element_by_class_name('long--name').text.lower()
        button = event.find_element_by_class_name('event--more')
        Page.click(button)
        url = Page.driver.current_url
        return Match(MatchTitle(name.split(' - ')), url, date_time, self)

    def _get_bets_one_by_one(self, sport_name):
        sport_bets = []
        matches = self.get_matches_info_sport(sport_name).matches

        for match in matches:
            Page('https://www.google.com/')
            print('match', matches.index(match) + 1, '/', len(matches))
            print(match.date)
            match_bets = FavoritScraper.scrape_match_bets(match)
            if match_bets:
                sport_bets.append(match_bets)
            break
        sport = Sport(sport_name, sport_bets)
        return sport

    def get_live_matches_info_sport(self, sport_name):
        matches = []
        Page(FavoritScraper._LIVE_URL)
        events = []
        events_ = [1, 2]
        time.sleep(2)

        while len(events) != len(events_):
            events = []
            events_ = None
            menu = Page.driver.find_element_by_class_name('sportslist')
            list_of_sports = menu.find_elements_by_class_name('sprt')
            sport = None
            for _sport in list_of_sports:
                if _sport.find_element_by_class_name('sprtnm').text == FavoritScraper._ICONS[sport_name]:
                    sport = _sport
                    break
            events_ = sport.find_elements_by_class_name('sp-mn-ev')
            for el in events_:
                try:
                    events.append(el.find_element_by_tag_name('div'))
                except Exception:
                    pass
            print(len(events_), len(events))

        for event in events:
            try:
                matches.append(self.get_live_match_basic_data(event))
            except Exception:
                pass
        return Sport(sport_name, matches)

    @staticmethod
    def get_live_match_basic_data(event):
        Page.click(event)
        teams = [name.text for name in event.find_elements_by_tag_name('span')]
        match_url = Page.driver.current_url

        return Match(MatchTitle(teams), match_url, '')


if __name__ == '__main__':
    t = time.time()
    scraper = FavoritScraper()
    sport = scraper.get_matches_info_sport(sport_name)
    print(sport)
    for match in sport:
        scraper.scrape_match_bets(match)
    # sport = scraper._get_bets_from_url('https://www.favorit.com.ua/en/bets/#event=27110455&tours=17296,18320,17294,17482,17295,17935,17944')
    print(sport)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + sport_name + '\\favorit.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', sport, file=f)

    print(time.time() - t)
