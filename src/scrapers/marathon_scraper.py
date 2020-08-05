import os.path

from selenium.common.exceptions import StaleElementReferenceException

from bet import Bet
from date_time import DateTime
from match import Match
from match_title import MatchTitle
from sport import Sport
from abstract_scraper import AbstractScraper
import time
from constants import sport_name
from src.renderer.page import Page
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


wait = WebDriverWait(Page.driver, 3)
tournament_names = None
country_names = None


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
    _LIVE_MENU = {
        'football': 'football',
        'csgo': 'e-sports',
        'dota': 'e-sports',
        'lol': 'e-sports'
    }
    _SKIP_TITLES = ['Goalscorers', 'Scorecast', '1st Goal + Full Time Result',
                    '1st Half + 2nd Half', '1st Half + Full Time\n',  # 'Correct Score',
                    '1st Half Result + 1st Half Total Goals', '1st Team to Score',
                    '2nd Half Result + 2nd Half Total Goals', 'Full Time Result + Total Goals',
                    'Goals + Half Result', 'Number of Goals', 'Penalty', '3 way',
                    'Order of Goals', 'Team To Score + Result', 'Score + Total',
                    '1st Team to Score', 'Goals Any Team To Score', 'Goals At Least One Team',
                    'Goals Both Teams To Score + Total', 'Corners', 'Yellow Cards', 'Fouls',
                    'Offsides', 'Goals Both Teams To Score + Total',
                    'Goals At Least One Team Not To Score + Total']

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
            print('tournament', tournaments.index(tournament) + 1, '/', len(tournaments))
            Page(tournament)
            matches = self.get_matches_from_tournament()
            for match in matches:
                print(' ' * 3, 'match', matches.index(match) + 1, '/', len(matches))
                match_bets = MarathonScraper._get_bets(match)
                if match_bets:
                    sport_bets.append(match_bets)
                break

        sport = Sport(sport_name, sport_bets)
        return sport

    @staticmethod
    def get_matches_from_tournament():
        return Page.driver.find_element_by_class_name('category-content').find_elements_by_class_name('bg')

    @staticmethod
    def get_live_matches_from_tournament():
        return wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'member-names-view')))

    @staticmethod
    def _get_live_match_basic_data(event):
        teams = [el.text for el in event.find_elements_by_class_name('member')]
        for team in teams:
            if '—' in team:
                teams.remove(team)
                team = team.replace('—', '')
                teams.append(team)

        Page.click(event)
        url = Page.driver.current_url
        Page.driver.back()
        return Match(MatchTitle(teams), url, '')

    @staticmethod
    def get_tournaments(sport_name):
        """
        Scrape match elements for a given sport type
        """
        Page(MarathonScraper._BASE_URL)
        icon = wait.until(EC.presence_of_element_located((By.CLASS_NAME, MarathonScraper._ICONS[sport_name])))
        # icon = page.driver.find_element_by_class_name(MarathonScraper._ICONS[sport_name])
        icon = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, MarathonScraper._ICONS[sport_name])))
        Page.click(icon)
        time.sleep(0.5)
        categories_icon = Page.driver.find_element_by_class_name('collapse-all-categories-checkbox')
        categories_icon = categories_icon.find_element_by_tag_name('input')
        Page.click(categories_icon)
        time.sleep(0.5)
        all_tournaments = Page.driver.find_elements_by_class_name('category-container')

        tournaments = []

        if MarathonScraper._MENU[sport_name]:
            # print(MarathonScraper._MENU[sport_name])
            for tournament in all_tournaments:
                try:
                    _sport_name = tournament.find_element_by_class_name('nowrap')
                except StaleElementReferenceException:
                    return MarathonScraper.get_tournaments(sport_name)
                if _sport_name.text == MarathonScraper._MENU[sport_name]:
                    tournaments.append(tournament)
        else:
            tournaments = all_tournaments

        if not MarathonScraper._MENU[sport_name]:
            if tournament_names:
                _tournaments = []
                for tournament_name in tournament_names:
                    _tournaments += [t for t in tournaments if tournament_name in t.text.lower()]
                for country_name in country_names:
                    _tournaments = [t for t in _tournaments if country_name in t.text.lower()]
                tournaments = _tournaments

        tournament_links = [t.find_element_by_class_name('category-label-link').get_attribute('href')
                            for t in tournaments]
        return tournament_links

    @staticmethod
    def _get_bets(event):
        bets = []
        match = MarathonScraper._get_match_basic_data(event)
        teams = match.title.teams
        main_odds = event.find_elements_by_class_name('selection-link')
        if len(main_odds) == 3:
            teams.insert(1, 'draw')
        bets += [Bet(
            teams[i] + ' will win',
            main_odds[i].text,
            MarathonScraper._NAME,
            match.url
        ) for i in range(len(teams))]

        try:
            match_button = event.find_element_by_class_name('event-more-view')
            Page.click(match_button)
            time.sleep(0.5)
        except Exception:
            return match

        try:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'details-description')))
            all_markets_button = element.find_element_by_tag_name('td')
            Page.click(all_markets_button)
        except Exception:
            return match
        time.sleep(0.5)
        try:
            MarathonScraper._parse_marketblocks(bets, match.url)
        except Exception:
            return match
        match.bets = bets
        Page.click(match_button)
        time.sleep(0.2)
        return match

    @staticmethod
    def _parse_marketblocks(bets, url):
        market_blocks = Page.driver.find_elements_by_class_name('market-inline-block-table-wrapper')
        for mb in market_blocks:
            try:
                block_title = mb.find_element_by_class_name('name-field').text
            except Exception:
                block_title = ''
                continue

            b = True
            for s in MarathonScraper._SKIP_TITLES:
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

    def _get_match_basic_data(self, match):
        date_time_str = match.find_element_by_class_name('date').text
        date_time = DateTime.from_marathon_str(date_time_str)
        url = match.find_element_by_class_name('member-link').get_attribute('href')
        teams = [el.text for el in match.find_elements_by_tag_name('span') if
                 el.get_attribute('data-member-link')]
        return Match(MatchTitle(teams), url, date_time, self)

    def get_matches_info_sport(self, sport_name):
        matches = []
        tournaments = self.get_tournaments(sport_name)
        print(self._NAME, 'scraping', len(tournaments), 'tournaments')
        # tournaments = [tournaments[0]]
        for tournament in tournaments:
            Page(tournament)
            print(' ', tournaments.index(tournament) + 1)
            events = self.get_matches_from_tournament()
            for event in events:
                matches.append(self._get_match_basic_data(event))
        return Sport(sport_name, matches)

    @staticmethod
    def _get_bets_from_url(match_url):
        Page(match_url)
        event = Page.driver.find_element_by_class_name('category-content').find_element_by_class_name('bg')
        # match = MarathonScraper._get_bets(event)
        bets = []
        match = MarathonScraper._get_match_basic_data(event)
        teams = match.title.teams
        main_odds = event.find_elements_by_class_name('selection-link')
        if len(main_odds) == 3:
            teams.insert(1, 'draw')
        bets += [Bet(
            teams[i] + ' will win',
            main_odds[i].text,
            MarathonScraper._NAME,
            match.url
        ) for i in range(len(teams))]

        try:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'details-description')))
            all_markets_button = element.find_element_by_tag_name('td')
            Page.click(all_markets_button)
        except Exception:
            return match
        time.sleep(0.5)
        try:
            MarathonScraper._parse_marketblocks(bets, match.url)
        except Exception:
            return match
        match.bets = bets
        time.sleep(0.2)
        return match

    def _get_bets_one_by_one(self, sport_name):
        sport_bets = []
        matches = self.get_matches_info_sport(sport_name).matches
        for match in matches:

            print('match', matches.index(match) + 1, '/', len(matches))
            print(match.date)
            match_bets = MarathonScraper.scrape_match_bets(match)
            if match_bets:
                sport_bets.append(match_bets)
            break
        sport = Sport(sport_name, sport_bets)
        return sport

    @staticmethod
    def scrape_match_bets(match):
        time.sleep(0.2)
        Page(match.url)
        try:
            teams = match.title.raw_teams
        except AttributeError:
            teams = match.title.teams

        main_odds = Page.driver.find_elements_by_class_name('selection-link')
        if len(main_odds) == 3:
            teams.insert(1, 'draw')
        match.bets += [Bet(
            teams[i] + ' will win',
            main_odds[i].text,
            MarathonScraper._NAME,
            match.url
        ) for i in range(len(teams))]

        try:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'details-description')))
            all_markets_button = element.find_element_by_tag_name('td')
            Page.click(all_markets_button)
        except Exception:
            return match

        time.sleep(0.5)

        try:
            MarathonScraper._parse_marketblocks(match.bets, match.url)
        except Exception:
            print('exception raised during parsing market blocks')
            return match
        return match

    @staticmethod
    def _get_bets_from_live_match_with_basic_data(match):
        Page(match.url)
        while True:
            bets = []
            try:
                MarathonScraper._parse_marketblocks(bets, match.url)
            except Exception:
                pass
            match.bets = bets
            # print_variable('live', MarathonScraper._NAME, 'match = ', match)
            time.sleep(0.5)

    def get_live_matches_info_sport(self, sport_name):
        matches = []
        tournaments = self.get_live_tournaments(sport_name)
        print(self._NAME, 'scraping', len(tournaments), 'tournaments')
        # tournaments = [tournaments[0]]
        for tournament in tournaments:
            Page(tournament)
            print(' ', tournaments.index(tournament) + 1)
            events = self.get_live_matches_from_tournament()
            for event in events:
                matches.append(self._get_live_match_basic_data(event))
        return Sport(sport_name, matches)

    @staticmethod
    def get_live_tournaments(sport_name):
        Page(MarathonScraper._BASE_URL + 'live')
        categories_icon = Page.driver.find_element_by_class_name('collapse-all-categories-checkbox')
        categories_icon = categories_icon.find_element_by_tag_name('input')
        Page.click(categories_icon)
        all_sports = Page.driver.find_elements_by_class_name('sport-category-header')
        my_sport = None
        for sport in all_sports:
            if MarathonScraper._LIVE_MENU[sport_name] in sport.text.lower():
                my_sport = sport
                break
        my_sport = my_sport.find_element_by_xpath('..')
        tournaments = my_sport.find_elements_by_class_name('category-label-link')
        if MarathonScraper._MENU[sport_name]:
            for tournament in list(tournaments):
                tournaments.remove(tournament)
                _sport_name = tournament.find_element_by_class_name('nowrap')
                if _sport_name.text == MarathonScraper._MENU[sport_name]:
                    tournaments.append(tournament)
        tournaments = [el.get_attribute('href') for el in tournaments]
        return tournaments


if __name__ == '__main__':
    t = time.time()
    scraper = MarathonScraper()
    sport = scraper.get_matches_info_sport(sport_name)
    print(sport)
    for match in sport:
        scraper.scrape_match_bets(match)
    # sport = scraper._get_bets_from_url('https://www.marathonbet.com/en/betting/Football/Clubs.+International/UEFA+Champions+League/Round+of+16/2nd+Leg/Juventus+vs+Lyon+-+9676474')
    print(sport)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + sport_name + '\\marathon.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', sport, file=f)
    print(time.time() - t)
