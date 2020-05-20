import re
import time
from pprint import pprint

from bs4 import BeautifulSoup

from src.renderer.page import Page
from src.scrapers.abstract_scraper import AbstractScraper
from syntax_formatters.syntax_formatter import SyntaxFormatter


class ParimatchScraper(AbstractScraper):
    """
    Class for scraping betting related information such as odds,
    match titles etc. from famous bookmaker website parimatch.com

    :param base_url: url of the front page of the website
    """
    base_url = 'https://www.parimatch.com/en'
    sport_names = {
        'csgo': 'counter-strike',
        'dota 2': 'dota-2',
    }
    # last titles for each of the groups
    title_breakers = ('Handicap coefficient', 'Under', 'Win of the 1st team',)

    def get_bets(self, sport_type):
        bets = {}

        championship_urls = ParimatchScraper.get_championship_urls(sport_type)
        for championship_url in championship_urls:
            bets.update(self._get_bets(self.base_url + championship_url))

        return bets

    @staticmethod
    def get_championship_urls(sport_type):
        """
        Scraps championship urls from the website

        :return: list of valid urls of all the championships on the website
        :rtype: str
        """
        page = Page('https://parimatch.com/sport/kibersport')
        soup = BeautifulSoup(page.html, 'html.parser')
        pattern = ParimatchScraper.sport_names[sport_type]
        championship_urls = [url.get('href') for url in soup.find_all('a', href=re.compile(pattern))]

        return championship_urls

    @staticmethod
    def _get_bets(url):
        """
        Scraps main betting data i.e match title, main bet titles and odds from the given soup

        :param soup: soup to scrape the bets from
        :type soup: BeautifulSoup
        :return: bets dictionary in the following form:
        bets[match_title][bet_title] = odds
        :rtype: dict
        """
        soup = ParimatchScraper._get_soup(url)
        bets = {}

        tag = soup.find(class_='processed')
        event_tag = tag.find(string='Event').parent
        bet_title_tags = event_tag.find_next_siblings()

        # main bets containers
        bks1 = [el.next_element for el in soup.find_all(class_='row1 processed')]
        bks2 = [el.next_element for el in soup.find_all(class_='row2 processed')]

        ParimatchScraper._parse_bks(bks1, bet_title_tags, bets)
        ParimatchScraper._parse_bks(bks2, bet_title_tags, bets)

        return bets

    @staticmethod
    def _parse_bks(bks, bet_title_tags, bets):
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
            Scraps main betting data i.e match title, bet titles and odds
            for given tag of class 'bk' and fills bets dict with it(data)

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
                        bets[match_title][subtitle + bet_titles_copy[i]] = odds[i]
                    except IndexError:
                        print(i)
                        print(bet_titles_copy)
                        print(odds)

                # reset bet titles
                if title in ParimatchScraper.title_breakers:
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
        Scraps match title found in the tag

        :param tag: one of the tags in parsed document created from the championship url's html
        :type tag: BeautifulSoup.Tag
        :return: match title in the form '<first team> - <second_team>'
        :rtype: str
        """
        br = tag.find(class_='l').find('br')

        first_team = br.previous_sibling
        if not isinstance(first_team, str):
            first_team = first_team.text
        second_team = br.next_sibling
        if not isinstance(second_team, str) and second_team is not None:
            second_team = second_team.text

        match_title = SyntaxFormatter.compile_match_title(first_team, second_team)

        return match_title

    @staticmethod
    def _get_soup(url):
        """
        Get soup of properly rendered page

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


t = time.time()
scraper = ParimatchScraper()

# bets = scraper.get_bets_all(url)
b = scraper.get_bets('csgo')
pprint(b)

Page.driver.quit()
print(time.time() - t)

# for url in urls:
#     try:
#         bets = ParimatchScraper.get_bets(url)
#         pprint(bets)
#     except OddsNotFoundError as e:
#         pprint(e.message)
#     except AttributeError:
#         pprint(url)
