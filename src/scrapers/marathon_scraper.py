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


class MarathonScraper(AbstractScraper):
    _NAME = 'marathon'
    _BASE_URL = 'https://www.marathonbet.com/en/'
    _MENU = {
        'csgo': 'CS:GO.',
        'dota': 'Dota 2.'
        }

    def get_sport_bets(self, sport_name):
        """
        Scrapes betting data for a given sport type

        :param sport_name: sport type to scrape betting data for
        :type sport_name: str
        """
        sport_bets = []
        matches = self.get_matches(sport_name)
        for match in matches:
            match_bets = MarathonScraper._get_bets(match)
            if match_bets:
                sport_bets.append(match_bets)

        sport = Sport(sport_name, sport_bets)
        return sport

    @staticmethod
    def get_matches(sport_name):
        """
        Scrape match elements for a given sport type
        """
        page = Page(MarathonScraper._BASE_URL)

        matches = []

        icon = page.driver.find_element_by_class_name('icon-sport-e-sports')
        page.click(icon)
        time.sleep(0.2)
        tournaments = page.driver.find_elements_by_class_name('category-container')
        for tournament in tournaments:
            _sport_name = tournament.find_element_by_class_name('nowrap')
            if _sport_name.get_attribute('innerHTML') == MarathonScraper._MENU[sport_name]:
                matches += tournament.find_elements_by_class_name('bg')

        return matches

    @staticmethod
    def _get_bets(match):
        bets = []
        url = match.find_element_by_class_name('member-link').get_attribute('href')
        teams = [el.get_attribute('innerHTML') for el in match.find_elements_by_tag_name('span') if
                 el.get_attribute('data-member-link')]
        match_title = MatchTitleCompiler.compile_match_title(*teams)
        if not match_title:
            return None

        main_odds = match.find_elements_by_class_name('selection-link')

        bets += [Bet(teams[i] + ' will win', main_odds[i].get_attribute('innerHTML')) for i in range(len(teams))]

        try:
            match_button = match.find_element_by_class_name('event-more-view')
            Page.click(match_button)
            time.sleep(0.5)
        except Exception:
            print('no more-view button', match_title)
            return None

        shortcuts = match.find_element_by_class_name('details-description')
        all_markets_button = shortcuts.find_element_by_tag_name('td')
        Page.click(all_markets_button)
        time.sleep(0.5)
        market_blocks = Page.driver.find_elements_by_class_name('market-inline-block-table-wrapper')
        for mb in market_blocks:
            block_title = mb.find_element_by_class_name('name-field').get_attribute('innerHTML')
            table = mb.find_element_by_class_name('td-border')
            results_left = mb.find_elements_by_class_name('result-left')
            another_results_left = table.find_elements_by_class_name('text-align-left')
            if results_left:
                odds = table.find_elements_by_class_name('result-right')
                for i in range(len(results_left)):
                    result_left = results_left[i].get_attribute('innerHTML')
                    o = odds[i].find_element_by_tag_name('span').get_attribute('innerHTML')
                    bet_title = block_title + ' ' + result_left
                    bet = Bet(bet_title, o)
                    bets.append(bet)

            elif another_results_left:
                teams = [el.find_element_by_tag_name('div').get_attribute('innerHTML') for el in
                         table.find_elements_by_class_name('width40')]
                # print(team)
                rows = table.find_elements_by_tag_name('tr')
                rows = rows[1:]
                for row in rows:
                    odds = row.find_elements_by_class_name('selection-link')
                    for i in range(len(odds)):
                        bet_type = row.find_element_by_class_name('text-align-left').get_attribute('innerHTML')
                        o = odds[i].get_attribute('innerHTML')
                        bet_title = block_title + ' ' + teams[i] + ' ' + bet_type
                        bet = Bet(bet_title, o)
                        bets.append(bet)

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
                            o = odds[i].get_attribute('innerHTML')
                            bet_title = block_title + ' ' + tags[i] + ' ' + bet_type
                            bet = Bet(bet_title, o)
                            bets.append(bet)

        match = Match(match_title, url, MarathonScraper._NAME, bets)

        Page.click(match_button)
        time.sleep(0.2)
        return match


if __name__ == '__main__':
    t = time.time()
    scraper = MarathonScraper()
    b = scraper.get_sport_bets(sport_name)
    pprint(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + sport_name + '\\marathon.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', pformat(b), file=f)
    print(time.time() - t)
