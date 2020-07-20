import os.path
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from bet import Bet
from match import Match
from sport import Sport
from abstract_scraper import AbstractScraper
from constants import sport_name
from match_title_compiler import MatchTitleCompiler
from src.renderer.page import Page


class FavoritScraper(AbstractScraper):
    _NAME = 'favorit'
    _BASE_URL = 'https://www.favorit.com.ua/en/bets/#'
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
                    'HT/FT'
                    ]

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
            match_buttons = self.get_match_buttons(subsection)
            for match_button in match_buttons:
                match_bets = FavoritScraper._get_bets(match_button)
                if match_bets:
                    sport_bets.append(match_bets)
                # break
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
            if sport.find_element_by_class_name('ttt').text == FavoritScraper._ICONS[sport_name]:
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
                if titles[i].text == FavoritScraper._SUBMENU[sport_name]:
                    return [checkboxes[i]]
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

        wait = WebDriverWait(Page.driver, 3)
        try:
            element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'slick-block')))
            Page.click(element)
        except Exception:
            pass
        time.sleep(0.5)
        market_blocks = Page.driver.find_elements_by_class_name('markets--block')
        for mb in market_blocks:
            block_title_head = mb.find_element_by_class_name('markets--head').get_attribute('innerHTML')

            b = True
            for s in FavoritScraper._SKIP_TITLES:
                if s in block_title_head:
                    b = False
                    break
            if not b:
                print(block_title_head)
                continue
            print(block_title_head)
            sub_block_titles = mb.find_elements_by_class_name('result--type--head')
            sub_blocks = mb.find_elements_by_class_name('outcome--list')
            for sub_block in sub_blocks:
                block_title_tail = ' ' + sub_block_titles[sub_blocks.index(sub_block)].find_element_by_tag_name(
                    'span').get_attribute('innerHTML')
                block_title = block_title_head + block_title_tail
                block = sub_block

                if mb.find_elements_by_class_name('mtype--7'):
                    break
                    # block = block.find_element_by_xpath('..')
                    # outcome_names = block.find_element_by_class_name('row--body').find_elements_by_class_name(
                    #     'outcome--name')
                    # names = []
                    # for outcome_name in outcome_names:
                    #     names.append(outcome_name.find_element_by_tag_name('span').get_attribute('innerHTML'))
                    # table = block.find_element_by_class_name('mtype--7')
                    # outcome_rows = table.find_elements_by_class_name('combo--outcome')
                    # for outcome_row in outcome_rows:
                    #     outcome_row_name = outcome_row.find_element_by_class_name('row--head').get_attribute(
                    #         'innerHTML')
                    #     odds = outcome_row.find_elements_by_tag_name('button')
                    #     for i in range(len(odds)):
                    #         bet_title = block_title + ' ' + outcome_row_name + ' ' + names[i]
                    #         bet = Bet(bet_title, odds[i].text, FavoritScraper._NAME, url)
                    #         bets.append(bet)
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
            teams = [el.text for el in init.find_elements_by_tag_name('span')]
            match_title = MatchTitleCompiler.compile_match_title(*teams)
        except Exception as e:
            print('mp not 1v1 match')
            return None

        return match_title

    @staticmethod
    def _get_bets_from_url(match_url):
        Page(match_url)
        bets = []
        # match_title = FavoritScraper._get_match_title()
        # if not match_title:
        #     return bets
        match_title = 'dadada'
        wait = WebDriverWait(Page.driver, 3)
        element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'slick-block')))
        Page.click(element)

        time.sleep(0.5)
        market_blocks = Page.driver.find_elements_by_class_name('markets--block')
        for mb in market_blocks:
            block_title_head = mb.find_element_by_class_name('markets--head').get_attribute('innerHTML')

            b = True
            for s in FavoritScraper._SKIP_TITLES:
                if s in block_title_head:
                    b = False
                    break
            if not b:
                print(block_title_head)
                continue

            sub_blocks = mb.find_elements_by_class_name('result--type--head')
            for sub_block in sub_blocks:
                block_title_tail = ' ' + sub_block.find_element_by_tag_name('span').get_attribute('innerHTML')
                block_title = block_title_head + block_title_tail
                block = sub_block

                if mb.find_elements_by_class_name('mtype--7'):
                    block = block.find_element_by_xpath('..')
                    outcome_names = block.find_element_by_class_name('row--body').find_elements_by_class_name(
                        'outcome--name')
                    names = []
                    for outcome_name in outcome_names:
                        names.append(outcome_name.find_element_by_tag_name('span').get_attribute('innerHTML'))
                    table = block.find_element_by_class_name('mtype--7')
                    outcome_rows = table.find_elements_by_class_name('combo--outcome')
                    for outcome_row in outcome_rows:
                        outcome_row_name = outcome_row.find_element_by_class_name('row--head').get_attribute(
                            'innerHTML')
                        odds = outcome_row.find_elements_by_tag_name('button')
                        for i in range(len(odds)):
                            bet_title = block_title + ' ' + outcome_row_name + ' ' + names[i]
                            bet = Bet(bet_title, odds[i].text, FavoritScraper._NAME, match_url)
                            bets.append(bet)
                else:
                    labels = block.find_elements_by_tag_name('label')
                    for label in labels:
                        if label.get_attribute('class') == 'outcome--empty':
                            continue
                        bet_type = label.find_element_by_tag_name('span').get_attribute('title')
                        bet_title = block_title + ' ' + bet_type
                        button = label.find_element_by_tag_name('button')
                        odds = button.text
                        bet = Bet(bet_title, odds, FavoritScraper._NAME, match_url)
                        bets.append(bet)

        match = Match(match_title, bets)
        return match

    def _get_urls_and_titles(self, sport_name):
        matches = []
        subsections = self.get_subsections(sport_name)
        for subsection in subsections:
            Page.click(subsection)
            table = Page.driver.find_element_by_class_name('category--list--block')
            events = table.find_elements_by_class_name('event--head-block')
            for event in events:
                name = event.find_element_by_class_name('long--name').text
                button = event.find_element_by_class_name('event--more')
                Page.click(button)
                url = Page.driver.current_url
                matches.append([name, url])


if __name__ == '__main__':
    t = time.time()
    scraper = FavoritScraper()
    b = scraper.get_sport_bets(sport_name)
    # b = scraper._get_bets_from_url('https://www.favorit.com.ua/en/bets/#event=27110455&tours=17296,18320,17294,17482,17295,17935,17944')
    print(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + sport_name + '\\favorit.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', b, file=f)

    print(time.time() - t)
