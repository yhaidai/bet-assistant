import re
import time
from pprint import pprint, pformat
import os.path
from bs4 import BeautifulSoup

# from parimatch_syntax_formatter import ParimatchSyntaxFormatter
from src.renderer.page import Page
from src.scrapers.abstract_scraper import AbstractScraper
from syntax_formatters.match_title_compiler import MatchTitleCompiler


class ParimatchScraper(AbstractScraper):
    """
    Class for scraping betting related information such as odds,
    match titles etc. from famous bookmaker website parimatch.com

    :param base_url: url of the front page of the website
    """
    _BASE_URL = 'https://www.parimatch.com/en'
    _SPORT_NAMES = {
        'csgo': 'counter-strike',
        'dota 2': 'dota-2',
        }
    _MENU = {
        'csgo': 'https://parimatch.com/sport/kibersport'
    }

    # last titles for each of the groups
    _TITLE_BREAKERS = ('Handicap coefficient', 'Under', 'Win of the 1st team',)

    def get_bets(self, sport_type):
        """
        Scrapes betting data for a given sport type

        :param sport_type: sport type to scrape betting data for
        :type sport_type: str
        """
        bets = {}

        championship_urls = ParimatchScraper.get_championship_urls(sport_type)
        for championship_url in championship_urls:
            bets.update(self._get_bets(self._BASE_URL + championship_url))

        return bets

    @staticmethod
    def get_championship_urls(sport_type):
        """
        Scrapes championship urls from the website

        :param sport_type: sport type to scrape championship urls for
        :type sport_type: str
        :return: list of urls of all the championships for the given sport type on the website
        :rtype: str
        """
        page = Page(ParimatchScraper._MENU[sport_type])
        soup = BeautifulSoup(page.html, 'html.parser')
        pattern = ParimatchScraper._SPORT_NAMES[sport_type]
        championship_urls = [url.get('href') for url in soup.find_all('a', href=re.compile(pattern))]

        return championship_urls

    @staticmethod
    def _get_bets(url):
        """
        Scrapes main betting data i.e match title, main bet titles and odds for the given championship url

        :param url: championship url to scrape the bets from
        :type url: str
        :return: bets dictionary in the following form: bets[match_title][bet_title] = odds
        :rtype: dict
        """
        print(url)
        soup = ParimatchScraper._get_soup(url)
        bets = {}

        tag = soup.find(class_='processed')
        event_tag = tag.find(string='Event')
        if not event_tag:
            return bets
        event_tag_parent = event_tag.parent
        bet_title_tags = event_tag_parent.find_next_siblings()

        # main bets containers
        bks1 = [el.next_element for el in soup.find_all(class_='row1 processed')]
        bks2 = [el.next_element for el in soup.find_all(class_='row2 processed')]

        ParimatchScraper._parse_bks(bks1, bet_title_tags, bets)
        ParimatchScraper._parse_bks(bks2, bet_title_tags, bets)

        return bets

    @staticmethod
    def _parse_bks(bks, bet_title_tags, bets):
        """
        Scrapes match title, bet titles and odds for given tags of class 'bk' and updates bets dict with scraped data

        :param bks: tags of class 'bk' and previous element of class 'row1 processed' or 'row2 processed'
        :type bks: list<BeautifulSoup.Tag>
        :param bet_title_tags: bet title tags of sport match belongs to
        :type bet_title_tags: list<BeautifulSoup.Tag>
        :param bets: dictionary storing betting data to updated
        :type bets: dict
        """
        for bk in bks:
            match_title = ParimatchScraper._get_match_title(bk)
            bets[match_title] = {}

            # get main bets for the match
            ParimatchScraper._update_bets(bk, bet_title_tags, match_title, '', bets)

            # get partial bets for the match if any
            row1_props = bk.parent.next_sibling
            if row1_props:
                props_bks = row1_props.find_all(class_='bk')
                if props_bks:
                    subtitle = props_bks[0].next_element.next_sibling.text + ' '
                    for props_bk in props_bks:
                        ParimatchScraper._update_bets(props_bk, bet_title_tags, match_title, subtitle, bets)

    @staticmethod
    def _update_bets(bk, bet_title_tags, match_title, subtitle, bets):
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
        :param bets: dictionary that stores betting data
        :type bets: dict
        """
        bet_titles = []
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

                # add odds info to bet titles and fill bets dictionary
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
                        bets[match_title][prefix + bet_titles_copy[i]] = odds[i]
                    except IndexError:
                        pass
                        # print(i)
                        # print(bet_titles_copy)
                        # print(odds)

                # reset bet titles
                if title in ParimatchScraper._TITLE_BREAKERS:
                    bet_titles = []

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

    b = scraper.get_bets('csgo')
    pprint(b)
    Page.driver.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\parimatch.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('bets = ', pformat(b), file=f)
    print(time.time() - t)
