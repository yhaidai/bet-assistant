import re
import time
from pprint import pprint, pformat
import os.path
from bs4 import BeautifulSoup

# from parimatch_syntax_formatter import ParimatchSyntaxFormatter
from Bet import Bet
from Match import Match
from Sport import Sport
from constants import sport_name
from src.renderer.page import Page
from src.scrapers.abstract_scraper import AbstractScraper
from syntax_formatters.match_title_compiler import MatchTitleCompiler


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
    _TITLE_BREAKERS = ('Handicap coefficient', 'Under', 'Win of the 1st team', )

    def get_sport_bets(self, sport_name):
        """
        Scrapes betting data for a given sport type

        :param sport_name: sport type to scrape betting data for
        :type sport_name: str
        """
        sport_bets = []

        championship_urls = ParimatchScraper.get_championship_urls(sport_name)
        championship_urls = championship_urls[:]

        for championship_url in championship_urls:
            full_url = self._BASE_URL + championship_url
            championship_bets = self._get_championship_bets(full_url)
            sport_bets += championship_bets

        sport = Sport(sport_name, sport_bets)
        return sport

    @staticmethod
    def get_championship_urls(sport_name):
        """
        Scrapes championship urls from the website

        :param sport_name: sport type to scrape championship urls for
        :type sport_name: str
        :return: list of urls of all the championships for the given sport type on the website
        :rtype: str
        """
        page = Page(ParimatchScraper._MENU[sport_name])
        soup = BeautifulSoup(page.html, 'html.parser')
        pattern = ParimatchScraper._SPORT_NAMES[sport_name] + '.+'
        championship_urls = [url.get('href') for url in soup.find_all('a', href=re.compile(pattern))]

        return championship_urls

    @staticmethod
    def _get_championship_bets(url):
        """
        Scrapes main betting data i.e match title, main bet titles and odds for the given championship url

        :param url: championship url to scrape the bets from
        :type url: str
        :return: bets dictionary in the following form: bets[match_title][bet_title] = odds
        :rtype: dict
        """
        print(url)
        soup = ParimatchScraper._get_soup(url)
        matches = []

        tag = soup.find(class_='processed')
        event_tag = tag.find(string='Event')
        if not event_tag:
            return matches
        event_tag_parent = event_tag.parent
        bet_title_tags = event_tag_parent.find_next_siblings()

        # main bets containers
        bks1 = [el.next_element for el in soup.find_all(class_='row1 processed')]
        bks2 = [el.next_element for el in soup.find_all(class_='row2 processed')]

        ParimatchScraper._parse_bks(bks1, bet_title_tags, matches, url)
        ParimatchScraper._parse_bks(bks2, bet_title_tags, matches, url)

        return matches

    @staticmethod
    def _parse_bks(bks, bet_title_tags, matches, url):
        """
        Scrapes match title, bet titles and odds for given tags of class 'bk' and updates bets dict with scraped data

        :param bks: tags of class 'bk' and previous element of class 'row1 processed' or 'row2 processed'
        :type bks: list<BeautifulSoup.Tag>
        :param bet_title_tags: bet title tags of sport match belongs to
        :type bet_title_tags: list<BeautifulSoup.Tag>
        :param matches: list storing betting data to be updated
        :type matches: list
        """
        for bk in bks:
            bets = []
            match_title = ParimatchScraper._get_match_title(bk)

            # get main bets for the match
            bets += ParimatchScraper._update_bets(bk, bet_title_tags, match_title, '', url)

            # get other bets for the match if any
            row1_props = bk.parent.next_sibling
            if row1_props:
                props_bks = row1_props.find_all(class_='bk')
                if props_bks:
                    subtitle_children_count = len(props_bks[0].contents)
                    for props_bk in props_bks:
                        if len(props_bk.contents) == subtitle_children_count:
                            subtitle = props_bk.next_element.next_sibling.text + ' '
                        bets += ParimatchScraper._update_bets(props_bk, bet_title_tags, match_title, subtitle, url)

            match = Match(match_title, bets)
            matches.append(match)

    @staticmethod
    def _update_bets(bk, bet_title_tags, match_title, subtitle, url):
        """
        Scrapes match title, bet titles and odds for given tag of class 'bk' and updates bets dict with scraped data

        :param bk: tag of class 'bk' to search column in
        :type bk: BeautifulSoup.Tag
        :param bet_title_tags: bet title tags of sport match belongs to
        :type bet_title_tags: list<BeautifulSoup.Tag>
        :param match_title: title of the match which bk belongs to
        :type match_title: str
        :param subtitle: subtitle for given bk
        :type subtitle: str
        :param matches: list that stores betting data
        :type matches: list
        """
        bet_titles = []
        bets = []
        team_names = MatchTitleCompiler.decompile_match_title(match_title)
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
                        if 'Handicap coefficient' in title:
                            prefix = subtitle + team_names[i] + ' '
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
        column = bk.next_element

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
        :rtype: str
        """
        br = tag.find(class_='l').find('br')

        first_team = br.previous_sibling
        if not isinstance(first_team, str):
            first_team = first_team.text
        second_team = br.next_sibling
        if not isinstance(second_team, str) and second_team is not None:
            second_team = second_team.text

        match_title = MatchTitleCompiler.compile_match_title(first_team, second_team)

        return match_title

    @staticmethod
    def _get_soup(url):
        """
        Get soup of rendered page

        :param url: url of the page soup of which is needed
        :type url: str
        :return: soup of the page which is located at given url
        :rtype: BeautifulSoup
        """
        page = Page(url)
        soup = BeautifulSoup(page.html, 'html.parser')

        while not ParimatchScraper._check_soup(soup):
            page = Page(url)
            soup = BeautifulSoup(page.html, 'html.parser')

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
    b = scraper.get_sport_bets(sport_name)
    pprint(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + sport_name + '\\parimatch.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', pformat(b), file=f)
    print(time.time() - t)
