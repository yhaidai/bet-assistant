import os.path
from bet import Bet
from match import Match
from sport import Sport
from abstract_scraper import AbstractScraper
import time
from constants import sport_name
from match_title_compiler import MatchTitleCompiler
from src.renderer.page import Page
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
wait = WebDriverWait(Page.driver, 3)


class MarathonScraper(AbstractScraper):
    _NAME = 'marathon'
    _BASE_URL = 'https://www.marathonbet.com/en/'
    _ICONS = {
        'football': 'icon-sport-football',
        'csgo': 'icon-sport-e-sports',
        'dota': 'icon-sport-e-sports',
        'lol': 'icon-sport-e-sports'
    }
    _MENU = {
        'football': None,
        'csgo': 'CS:GO.',
        'dota': 'Dota 2.',
        'lol': 'LoL.'
    }

    def get_sport_bets(self, sport_name):
        """
        Scrapes betting data for a given sport type

        :param sport_name: sport type to scrape betting data for
        :type sport_name: str
        """
        sport_bets = []
        tournaments = self.get_tournaments(sport_name)

        # tournaments = [tournaments[0]]
        for tournament in tournaments:
            matches = self.get_matches_from_tournament(tournament)
            for match in matches:
                match_bets = MarathonScraper._get_bets(match, tournament)
                if match_bets:
                    sport_bets.append(match_bets)

        sport = Sport(sport_name, sport_bets)
        return sport

    @staticmethod
    def get_matches_from_tournament(tournament):
        return tournament.find_element_by_class_name('category-content').find_elements_by_class_name('bg')

    @staticmethod
    def get_tournaments(sport_name):
        """
        Scrape match elements for a given sport type
        """
        page = Page(MarathonScraper._BASE_URL)

        icon = page.driver.find_element_by_class_name(MarathonScraper._ICONS[sport_name])
        page.click(icon)
        time.sleep(0.5)
        categories_icon = Page.driver.find_element_by_class_name('collapse-all-categories-checkbox')
        categories_icon = categories_icon.find_element_by_tag_name('input')
        page.click(categories_icon)
        time.sleep(0.5)
        all_tournaments = Page.driver.find_elements_by_class_name('category-container')

        tournaments = []

        if MarathonScraper._MENU[sport_name]:
            print(MarathonScraper._MENU[sport_name])
            for tournament in all_tournaments:
                _sport_name = tournament.find_element_by_class_name('nowrap')
                if _sport_name.text == MarathonScraper._MENU[sport_name]:
                    tournaments.append(tournament)
        else:
            tournaments = all_tournaments

        if not MarathonScraper._MENU[sport_name]:
            if tournament_names:
                _tournaments = []
                for tournament_name in tournament_names:
                    _tournaments += [t for t in tournaments if tournament_name in t.text.lower()]
                tournaments = _tournaments

        for tournament in tournaments:
            collapse_button = tournament.find_element_by_class_name('collapse-button')
            Page.click(collapse_button)
            time.sleep(0.1)

        all_tournaments = Page.driver.find_elements_by_class_name('category-container')
        _tournaments = []
        for t in list(all_tournaments):
            if 'collapsed' in t.get_attribute('class'):
                all_tournaments.remove(t)
        tournaments = all_tournaments

        return tournaments

    @staticmethod
    def _get_bets(match, tournament):
        bets = []
        url = match.find_element_by_class_name('member-link').get_attribute('href')
        teams = [el.text for el in match.find_elements_by_tag_name('span') if
                 el.get_attribute('data-member-link')]
        match_title = MatchTitleCompiler.compile_match_title(*teams)
        if not match_title:
            return None

        main_odds = match.find_elements_by_class_name('selection-link')
        if len(main_odds) == 3:
            teams.insert(1, 'draw')
        bets += [Bet(
            teams[i] + ' will win',
            main_odds[i].text,
            MarathonScraper._NAME,
            url
        ) for i in range(len(teams))]

        try:
            match_button = match.find_element_by_class_name('event-more-view')
            Page.click(match_button)
            time.sleep(0.5)
        except Exception:
            return Match(match_title, bets)

        try:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'details-description')))
            all_markets_button = element.find_element_by_tag_name('td')
            Page.click(all_markets_button)
        except Exception:
            return None
        time.sleep(0.5)
        try:
            market_blocks = tournament.find_elements_by_class_name('market-inline-block-table-wrapper')
            for mb in market_blocks:
                try:
                    block_title = mb.find_element_by_class_name('name-field').text
                except Exception:
                    block_title = ''
                    continue

                b = True
                for s in skip:
                    if s in block_title:
                        b = False
                        break
                if not b:
                    # print(block_title)
                    continue

                table = mb.find_element_by_class_name('td-border')
                results_left = mb.find_elements_by_class_name('result-left')
                another_results_left = table.find_elements_by_class_name('text-align-left')
                if results_left:
                    odds = table.find_elements_by_class_name('result-right')
                    for i in range(len(results_left)):
                        result_left = results_left[i].text
                        o = odds[i].find_element_by_tag_name('span').text
                        bet_title = block_title + ' ' + result_left
                        bet = Bet(bet_title, o, MarathonScraper._NAME, url)
                        bets.append(bet)
                elif another_results_left:
                    tags = [el.text for el in table.find_elements_by_tag_name('th')[1:]]
                    rows = table.find_elements_by_tag_name('tr')
                    rows = rows[1:]
                    for row in rows:
                        odds = row.find_elements_by_class_name('selection-link')
                        for i in range(len(odds)):
                            bet_type = row.find_element_by_class_name('text-align-left').text
                            o = odds[i].text
                            bet_title = block_title + ' ' + bet_type + ' ' + tags[i]
                            bet = Bet(bet_title, o, MarathonScraper._NAME, url)
                            if 'Score + Total' not in bet_type:
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
                            tags = [tag_raw.text for tag_raw in tags_raw]
                        else:
                            cells = row.find_elements_by_class_name('height-column-with-price')
                            empty_cells = []
                            for cell in cells:
                                if 'td-min-width' in cell.get_attribute('class'):
                                    empty_cells.append(cells.index(cell))
                            bet_types = row.find_elements_by_class_name('coeff-value')
                            odds = row.find_elements_by_class_name('selection-link')
                            for i in range(len(odds)):
                                if i not in empty_cells:
                                    bet_type = ''
                                    if bet_types:
                                        bet_type = bet_types[i].text
                                    o = odds[i].text
                                    bet_title = block_title + ' ' + bet_type + ' ' + tags[i]
                                    bet = Bet(bet_title, o, MarathonScraper._NAME, url)
                                    bets.append(bet)
        except Exception:
            return Match(match_title, bets)
        match = Match(match_title, bets)
        Page.click(match_button)
        time.sleep(0.2)
        return match

    @staticmethod #musor
    def _get_bets_from_url(match_url):
        Page(match_url)
        time.sleep(1)
        bets = []
        match = Page.driver.find_element_by_class_name('category-content').find_element_by_class_name('bg')
        teams = [el.text for el in match.find_elements_by_tag_name('span') if
                 el.get_attribute('data-member-link')]
        match_title = MatchTitleCompiler.compile_match_title(*teams)
        if not match_title:
            return None
        main_odds = match.find_elements_by_class_name('selection-link')
        bets += [Bet(
            teams[i] + ' will win',
            main_odds[i].text,
            MarathonScraper._NAME,
            match_url
        ) for i in range(len(teams))]

        # try:
        #     match_button = match.find_element_by_class_name('event-more-view')
        #     Page.click(match_button)
        #     time.sleep(0.5)
        # except Exception:
        #     print('no more-view button', match_title)
        #     return None

        shortcuts = Page.driver.find_element_by_class_name('table-shortcuts-menu')
        all_markets_button = shortcuts.find_element_by_tag_name('td')
        Page.click(all_markets_button)
        time.sleep(0.5)
        blocks = Page.driver.find_element_by_class_name('block-market-wrapper')
        market_blocks = blocks.find_elements_by_class_name('market-inline-block-table-wrapper')
        for mb in market_blocks:
            try:
                block_title = mb.find_element_by_class_name('name-field').text
            except Exception:
                continue

            b = True
            for s in skip:
                if s in block_title:
                    b = False
                    break
            if not b:
                # print(block_title)
                continue

            table = mb.find_element_by_class_name('td-border')
            results_left = mb.find_elements_by_class_name('result-left')
            another_results_left = table.find_elements_by_class_name('text-align-left')
            if results_left:
                odds = table.find_elements_by_class_name('result-right')
                for i in range(len(results_left)):
                    result_left = results_left[i].text
                    o = odds[i].find_element_by_tag_name('span').text
                    bet_title = block_title + ' ' + result_left
                    bet = Bet(bet_title, o, MarathonScraper._NAME, match_url)
                    bets.append(bet)
            elif another_results_left:
                tags = [el.text for el in table.find_elements_by_tag_name('th')[1:]]
                rows = table.find_elements_by_tag_name('tr')
                rows = rows[1:]
                for row in rows:
                    odds = row.find_elements_by_class_name('selection-link')
                    for i in range(len(odds)):
                        bet_type = row.find_element_by_class_name('text-align-left').text
                        o = odds[i].text
                        bet_title = block_title + ' ' + bet_type + ' ' + tags[i]
                        bet = Bet(bet_title, o, MarathonScraper._NAME, match_url)
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
                        tags = [tag_raw.text for tag_raw in tags_raw]
                    else:
                        cells = row.find_elements_by_class_name('height-column-with-price')
                        empty_cells = []
                        for cell in cells:
                            if 'td-min-width' in cell.get_attribute('class'):
                                empty_cells.append(cells.index(cell))
                        bet_types = row.find_elements_by_class_name('coeff-value')
                        odds = row.find_elements_by_class_name('selection-link')
                        for i in range(len(odds)):
                            if i not in empty_cells:
                                bet_type = ''
                                if bet_types:
                                    bet_type = bet_types[i].text
                                o = odds[i].text
                                bet_title = block_title + ' ' + bet_type + ' ' + tags[i]
                                bet = Bet(bet_title, o, MarathonScraper._NAME, match_url)
                                bets.append(bet)
        match = Match(match_title, bets)
        return match


if __name__ == '__main__':
    t = time.time()
    scraper = MarathonScraper()
    b = scraper.get_sport_bets(sport_name)
    # b = scraper._get_bets_from_url('https://www.marathonbet.com/en/betting/Football/Clubs.+International/UEFA+Champions+League/Round+of+16/2nd+Leg/Juventus+vs+Lyon+-+9676474')
    print(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + sport_name + '\\marathon.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', b, file=f)
    print(time.time() - t)
