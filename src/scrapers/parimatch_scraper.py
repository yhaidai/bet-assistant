import os.path
import pickle
import re
import sys
import time

from bs4 import BeautifulSoup

from bet import Bet
from constants import sport_name
from date_time import DateTime
from match import Match
from match_title import MatchTitle
from sport import Sport
from src.scrapers.abstract_scraper import AbstractScraper


class ParimatchScraper(AbstractScraper):
    """
    Class for scraping betting related information such as odds,
    match titles etc. from famous bookmaker website parimatch.com

    :param base_url: url of the front page of the website
    """
    _NAME = 'parimatch'
    _BASE_URL = 'https://www.parimatch.com/en'
    _SPORT_NAMES = {
        'csgo': 'counter-strike',
        'dota': 'dota-2',
        'football': 'futbol',
        'lol': 'liga-legend',
        }
    _MENU = {
        'csgo': 'https://parimatch.com/sport/kibersport',
        'dota': 'https://parimatch.com/sport/kibersport',
        'football': 'https://parimatch.com/sport/futbol',
        'lol': 'https://parimatch.com/sport/kibersport',
        }

    # last titles for each of the groups
    _TITLE_BREAKERS = ('Handicap coefficient', 'Under', 'Win of the 1st team',)

    def get_name(self) -> str:
        return self._NAME

    def get_matches_info_sport(self, sport_name):
        sport_matches = []

        championship_urls = self.get_championship_urls(sport_name)
        for championship_url in championship_urls[:]:
            if 'statistika' in championship_url:
                continue
            full_url = self._BASE_URL + championship_url
            championship_matches = self._get_championship_matches_info(full_url)
            sport_matches += championship_matches

        sport = Sport(sport_name, sport_matches)
        return sport

    def get_championship_urls(self, sport_name):
        """
        Scrapes championship urls from the website

        :param sport_name: sport type to scrape championship urls for
        :type sport_name: str
        :return: list of urls of all the championships for the given sport type on the website
        :rtype: str
        """
        self.renderer.get(ParimatchScraper._MENU[sport_name])
        soup = BeautifulSoup(self.renderer.page_source, 'html.parser')
        pattern = ParimatchScraper._SPORT_NAMES[sport_name] + '.+'
        championship_urls = {a.get('href') for a in soup.find_all('a', href=re.compile(pattern))}

        return list(championship_urls)

    def _get_championship_matches_info(self, url):
        soup = self._get_soup(url)
        matches = []
        bks = self._get_bks(soup)

        for bk in bks:
            match_title = ParimatchScraper._get_match_title(bk)
            date_time_str = ParimatchScraper._get_match_date_time_str(bk)
            date_time = DateTime.from_parimatch_str(date_time_str)
            match = Match(match_title, url, date_time, self)
            match.id = bk.find(class_='no').text
            matches.append(match)

        return matches

    @staticmethod
    def _get_bks(soup: BeautifulSoup):
        bks1 = [el.next_element for el in soup.find_all(class_='row1 processed')]
        bks2 = [el.next_element for el in soup.find_all(class_='row2 processed')]
        bks = bks1 + bks2
        return bks

    def _get_match_bk(self, soup: BeautifulSoup, match: Match):
        bks = ParimatchScraper._get_bks(soup)
        for bk in bks:
            if bk.find(class_='no').text == match.id:
                return bk

        print('Couldn\'t find bk with id', match.id, self.renderer.current_url)
        return None

    def scrape_match_bets(self, match: Match):
        soup = self._get_soup(match.url)
        bk = self._get_match_bk(soup, match)

        event_tag = soup.find(class_='processed').find(string='Event')
        if not event_tag:
            return match
        bet_title_tags = event_tag.parent.find_next_siblings()

        # get main bets for the match
        match.bets += ParimatchScraper._update_bets(bk, bet_title_tags, match.title, '', match.url)

        # get other bets for the match if any
        row1_props = bk.parent.next_sibling
        if row1_props:
            props_bks = row1_props.find_all(class_='bk')
            if props_bks:
                subtitle_children_count = len(props_bks[0].contents)
                for props_bk in props_bks:
                    if len(props_bk.contents) == subtitle_children_count:
                        if props_bk.next_element.next_sibling.text != '\xa0':
                            subtitle = props_bk.next_element.next_sibling.text + ' '
                    match.bets += ParimatchScraper._update_bets(props_bk, bet_title_tags, match.title, subtitle,
                                                                match.url)

    @staticmethod
    def _update_bets(bk, bet_title_tags, match_title, subtitle, url):
        """
        Scrapes match title, bet titles and odds for given tag of class 'bk' and updates bets dict with scraped data

        :param bk: tag of class 'bk' to search column in
        :type bk: BeautifulSoup.Tag
        :param bet_title_tags: bet title tags of sport match belongs to
        :type bet_title_tags: list<BeautifulSoup.Tag>
        :param match_title: title of the match which bk belongs to
        :type match_title: MatchTitle
        :param subtitle: subtitle for given bk
        :type subtitle: str
        :param matches: list that stores betting data
        :type matches: list
        """
        bet_titles = []
        bets = []
        try:
            teams = match_title.raw_teams
        except AttributeError:
            teams = match_title.teams

        for bet_title_tag in bet_title_tags:
            # find corresponding column with bet type
            column = ParimatchScraper._find_column(bk, bet_title_tag)

            # found column has no info - continue
            if not column:
                continue

            # get title
            try:
                title = bet_title_tag['title']
            except KeyError:
                title = bet_title_tag.text

            # find bet types and add them to bet titles if any
            bet_types = [el.text for el in column.find_all('b')]
            if bet_types:
                for bet_type in bet_types:
                    bet_titles.append(title + '. ' + bet_type + '. ')
            # if column contains odds(doesn't contain bet types)
            else:
                bet_titles_copy = bet_titles.copy()
                odds = [el.text for el in column.find_all('a')]

                # odds might be inactive
                if not odds:
                    odds = [el.text for el in column.find_all('s')]

                # if there are no bet titles make bet titles from odds info only
                if not bet_titles_copy:
                    bet_titles_copy = ['' for o in odds]

                # add odds info to bet titles and fill bets list
                for i in range(len(bet_titles_copy)):
                    try:
                        bet_titles_copy[i] += bet_title_tag['title']
                    except KeyError:
                        bet_titles_copy[i] += bet_title_tag.text
                    try:
                        prefix = subtitle
                        # append team name to the subtitle in case of handicap bet
                        if 'Handicap coefficient' in title or 'Team totals' in bet_titles_copy[i]:
                            prefix = subtitle + teams[i] + ' '
                        bet = Bet(prefix + bet_titles_copy[i], odds[i], ParimatchScraper._NAME, url)
                        bets.append(bet)
                    except IndexError:
                        pass
                        # print(i)
                        # print(bet_titles_copy)
                        # print(odds)

                # reset bet titles
                if title in ParimatchScraper._TITLE_BREAKERS:
                    bet_titles = []

        return bets

    @staticmethod
    def _find_column(bk, bet_title_tag):
        """
        Finds 'td' tag that is under the given bet title tag or None if such tag is empty

        :param bk: tag of class 'bk' to search column in
        :type bk: BeautifulSoup.Tag
        :param bet_title_tag: bet title tag to search corresponding bet type column to
        :type bet_title_tag: BeautifulSoup.Tag
        :return: 'td' tag that is under the given bet title tag
        :rtype: BeautifulSoup.Tag
        """
        try:
            column = bk.next_element
        except AttributeError:
            return None

        try:
            skip = int(column['colspan'])
        except KeyError:
            skip = 0

        for sibling in bet_title_tag.find_previous_siblings():
            skip -= 1
            if skip <= 0:
                column = column.next_sibling
                try:
                    skip = int(column['colspan'])
                except KeyError:
                    skip = 0
                except TypeError:
                    print('NoneType is not subscriptable, bet title:', bet_title_tag.text)
                    time.sleep(30)
                    return ParimatchScraper._find_column(bk, bet_title_tag)

        if skip > 0:
            return None

        return column

    @staticmethod
    def _get_match_title(tag):
        """
        Scrapes match title found in the tag

        :param tag: one of the tags in parsed document created from the championship url's html
        :type tag: BeautifulSoup.Tag
        :return: match title in the form 'first team - second_team'
        :rtype: MatchTitle
        """
        br = tag.find(class_='l').find('br')
        teams = []

        first_team = br.previous_sibling
        if not isinstance(first_team, str):
            first_team = first_team.text
        teams.append(first_team)

        second_team = br.next_sibling
        if not isinstance(second_team, str) and second_team is not None:
            second_team = second_team.text
        if second_team:
            teams.append(second_team)

        match_title = MatchTitle(teams)

        return match_title

    @staticmethod
    def _get_match_date_time_str(tag):
        br = tag.find('td').next_sibling.find('br')
        return br.previous_sibling + br.next_sibling

    def _get_soup(self, url):
        """
        Get soup of rendered page

        :param url: url of the page soup of which is needed
        :type url: str
        :return: soup of the page which is located at given url
        :rtype: BeautifulSoup
        """
        self.renderer.get(url)
        soup = BeautifulSoup(self.renderer.page_source, 'html.parser')

        while not ParimatchScraper._check_soup(soup) or self.renderer.current_url == 'https://www.pm-511.info/':
            if self.renderer.current_url == 'https://www.pm-511.info/':
                print('page.driver.current_url == https://www.pm-511.info/')
            self.renderer.get(url)
            soup = BeautifulSoup(self.renderer.page_source, 'html.parser')

        return soup

    @staticmethod
    def _check_soup(soup):
        """
        Checks if page was properly rendered using its soup

        :param soup: soup that needs to be checked
        :type soup: BeautifulSoup
        :return: True if tag with class 'processed' is found, False otherwise
        :rtype: boolean
        """
        tag = soup.find(class_='processed')
        if tag is None:
            return False
        return True


if __name__ == '__main__':
    t = time.time()
    scraper = ParimatchScraper()

    sport = scraper.get_matches_info_sport(sport_name)
    # for match in sport:
    #     print(match.url)
    #     scraper.scrape_match_bets(match)
    print(sport)

    scraper.renderer.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + sport_name + '\\' + scraper.get_name()
    print(path)
    sport.serialize(path)
    with open(path + '.py', 'w', encoding='utf-8') as f:
        print('sport =', sport, file=f)
    print(time.time() - t)
