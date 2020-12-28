import os.path

from selenium.common.exceptions import StaleElementReferenceException

from bet import Bet
from date_time import DateTime
from match import Match
from match_title import MatchTitle
from sport import Sport
from abstract_scraper import AbstractScraper
import time
from constants import SPORT_NAME
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


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

    def get_name(self) -> str:
        return self._NAME

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
            self.renderer.get(tournament)
            matches = self.get_matches_from_tournament()
            for match in matches:
                print(' ' * 3, 'match', matches.index(match) + 1, '/', len(matches))
                match_bets = self._get_bets(match)
                if match_bets:
                    sport_bets.append(match_bets)
                break

        sport = Sport(sport_name, sport_bets)
        return sport

    def get_matches_from_tournament(self):
        return self.renderer.find_element_by_class_name('category-content').find_elements_by_class_name('bg')

    def get_live_matches_from_tournament(self):
        return self.renderer.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'member-names-view')))

    def _get_live_match_basic_data(self, event):
        teams = [el.text for el in event.find_elements_by_class_name('member')]
        for team in teams:
            if '—' in team:
                teams.remove(team)
                team = team.replace('—', '')
                teams.append(team)

        self.renderer.click(event)
        url = self.renderer.current_url
        self.renderer.back()
        return Match(MatchTitle(teams), url, None, self)

    def get_tournaments(self, sport_name):
        """
        Scrape match elements for a given sport type
        """
        self.renderer.get(MarathonScraper._BASE_URL)
        icon = self.renderer.wait.until(EC.presence_of_element_located((By.CLASS_NAME, MarathonScraper._ICONS[sport_name])))
        # icon = self.renderer.find_element_by_class_name(MarathonScraper._ICONS[sport_name])
        icon = self.renderer.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, MarathonScraper._ICONS[sport_name])))
        self.renderer.click(icon)
        time.sleep(0.5)
        categories_icon = self.renderer.find_element_by_class_name('collapse-all-categories-checkbox')
        categories_icon = categories_icon.find_element_by_tag_name('input')
        self.renderer.click(categories_icon)
        time.sleep(0.5)
        all_tournaments = self.renderer.find_elements_by_class_name('category-container')

        tournaments = []

        if MarathonScraper._MENU[sport_name]:
            # print(MarathonScraper._MENU[sport_name])
            for tournament in all_tournaments:
                try:
                    _sport_name = tournament.find_element_by_class_name('nowrap')
                    if _sport_name.text == MarathonScraper._MENU[sport_name]:
                        tournaments.append(tournament)
                except StaleElementReferenceException:
                    return self.get_tournaments(sport_name)
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

    def _get_bets(self, event):
        bets = []
        match = self._get_match_basic_data(event)
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
            self.renderer.click(match_button)
            time.sleep(0.5)
        except Exception:
            return match

        try:
            element = self.renderer.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'details-description')))
            all_markets_button = element.find_element_by_tag_name('td')
            self.renderer.click(all_markets_button)
        except Exception:
            return match
        time.sleep(0.5)
        try:
            self._parse_marketblocks(bets, match.url)
        except Exception:
            return match
        match.bets = bets
        self.renderer.click(match_button)
        time.sleep(0.2)
        return match

    def _parse_marketblocks(self, bets, url):
        soup = self.renderer.soup()
        market_blocks = soup.find_all(class_='market-inline-block-table-wrapper')
        for mb in market_blocks:
            try:
                block_title = mb.find(class_='name-field').text
            except AttributeError:
                # TODO: check next line istead of continue
                # block_title = ''
                continue

            b = True
            for s in MarathonScraper._SKIP_TITLES:
                if s in block_title:
                    b = False
                    break
            if not b:
                continue

            table = mb.find(class_='td-border')
            results_left = mb.find_all(class_='result-left')
            another_results_left = table.find_all(class_='text-align-left')
            if results_left:
                odds = table.find_all(class_='result-right')
                for i in range(len(results_left)):
                    result_left = results_left[i].text
                    o = odds[i].find('span').text
                    bet_title = block_title + ' ' + result_left
                    bet = Bet(bet_title, o, MarathonScraper._NAME, url)
                    bets.append(bet)
            elif another_results_left:
                tags = [el.text for el in table.find_all('th')[1:]]
                rows = table.find_all('tr')
                rows = rows[1:]
                for row in rows:
                    odds = row.find_all(class_='selection-link')
                    for i in range(len(odds)):
                        bet_type = row.find(class_='text-align-left').text
                        o = odds[i].text
                        bet_title = block_title + ' ' + bet_type + ' ' + tags[i]
                        bet = Bet(bet_title, o, MarathonScraper._NAME, url)
                        if 'Score + Total' not in bet_type:
                            bets.append(bet)
            else:
                rows = table.find_all('tr')
                for row in rows:
                    tags_raw = row.find_all('th')
                    if tags_raw:
                        for i in range(len(tags_raw)):
                            tag_raw_div = tags_raw[i].find('div')
                            if not tag_raw_div:
                                break
                            else:
                                tags_raw[i] = tag_raw_div
                        tags = [tag_raw.text for tag_raw in tags_raw if tag_raw]
                    else:
                        cells = row.find_all(class_='height-column-with-price')
                        empty_cells = []
                        for cell in cells:
                            if 'td-min-width' in cell.get('class'):
                                empty_cells.append(cells.index(cell))
                        bet_types = row.find_all(class_='coeff-value')
                        odds = row.find_all(class_='selection-link')
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
        for tournament in tournaments[:]:
            self.renderer.get(tournament)
            print(' ', tournaments.index(tournament) + 1)
            events = self.get_matches_from_tournament()
            for event in events:
                matches.append(self._get_match_basic_data(event))
        return Sport(sport_name, matches)

    @staticmethod
    def _get_bets_from_url(self, match_url):
        self.renderer(match_url)
        event = self.renderer.find_element_by_class_name('category-content').find_element_by_class_name('bg')
        # match = self._get_bets(event)
        bets = []
        match = self._get_match_basic_data(event)
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
            element = self.renderer.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'details-description')))
            all_markets_button = element.find_element_by_tag_name('td')
            self.renderer.click(all_markets_button)
        except Exception:
            return match
        time.sleep(0.5)
        try:
            self._parse_marketblocks(bets, match.url)
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

    def scrape_match_bets(self, match):
        t = time.time()
        self.renderer.get(match.url)
        try:
            teams = match.title.raw_teams
        except AttributeError:
            teams = match.title.teams

        main_row = self.renderer.find_element_by_class_name('sub-row')
        main_odds = main_row.find_elements_by_class_name('selection-link')

        main_bet_titles = ['Result ' + team + ' To Win' for team in teams]
        if len(main_odds) == 3:
            main_bet_titles.insert(1, 'Result Draw')

        match.bets += [Bet(
            main_bet_titles[i],
            main_odds[i].text,
            MarathonScraper._NAME,
            match.url
            ) for i in range(len(teams))]
        try:
            element = self.renderer.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'details-description')))
            all_markets_button = element.find_element_by_tag_name('td')
            self.renderer.click(all_markets_button)
        except Exception:
            print(self._NAME, time.time() - t)
            return match
        self._parse_marketblocks(match.bets, match.url)
        print(self._NAME, time.time() - t)
        return match

    def _get_bets_from_live_match_with_basic_data(self, match):
        self.renderer.get(match.url)
        while True:
            bets = []
            try:
                self._parse_marketblocks(bets, match.url)
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
            self.renderer.get(tournament)
            print(' ', tournaments.index(tournament) + 1)
            events = self.get_live_matches_from_tournament()
            for event in events:
                matches.append(self._get_live_match_basic_data(event))
        return Sport(sport_name, matches)

    def get_live_tournaments(self, sport_name):
        self.renderer.get(MarathonScraper._BASE_URL + 'live')
        categories_icon = self.renderer.find_element_by_class_name('collapse-all-categories-checkbox')
        categories_icon = categories_icon.find_element_by_tag_name('input')
        self.renderer.click(categories_icon)
        all_sports = self.renderer.find_elements_by_class_name('sport-category-header')
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
    sport = scraper.get_matches_info_sport(SPORT_NAME)
    # for match in sport[:2]:
    #     scraper.scrape_match_bets(match)
    print(sport)
    scraper.renderer.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + SPORT_NAME + '\\' + scraper.get_name()
    sport.serialize(path)
    with open(path + '.py', 'w', encoding='utf-8') as f:
        print('sport =', sport, file=f)
    print(time.time() - t)
