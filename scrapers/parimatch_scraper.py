from bs4 import BeautifulSoup
from renderer.page import Page
from pprint import pprint
from syntax_formatters.syntax_formatter import ParimatchSyntaxFormatter
from exceptions.scraping_unsuccessful_exception import \
    ScrapingUnsuccessfulException
from exceptions.odds_not_found_error import OddsNotFoundError


class ParimatchScraper:
    """
    Class for scraping betting related information such as odds,
    match titles etc. from famous bookmaker website parimatch.com

    :param base_url: url of the front page of the website
    """
    base_url = 'https://www.parimatch.com/en'

    @staticmethod
    def get_championships_urls():
        """
        Scraps championship urls from the website

        :return: list of valid urls of all the championships on the website
        :rtype: str
        """
        urls = []
        page = Page(ParimatchScraper.base_url)
        soup = BeautifulSoup(page.html, 'html.parser')

        hidden_groups = soup.find_all('ul', class_='hidden groups')
        for group in hidden_groups:
            for tag in group.find_all('a'):
                urls.append(ParimatchScraper.base_url[:-1] + tag['href'])
        return urls

    @staticmethod
    def get_bets(url):
        """
        Scraps data such as match titles, bet titles and odds from the given url

        :param url: any valid championship url on the website
        :type url: str
        :return: bets dictionary in the following form:
        bets[match_title][bet_title] = odds
        :rtype: dict
        """
        bets = {}
        page = Page(url)
        soup = BeautifulSoup(page.html, 'html.parser')

        match_titles = ParimatchScraper._get_match_titles(soup)
        bet_titles = ParimatchScraper._get_bet_titles(soup)
        other_titles_count = ParimatchScraper._get_other_titles_count(soup)
        odds = ParimatchScraper._get_odds(soup, other_titles_count)

        # pprint(match_titles)
        # pprint(bet_titles)
        # pprint(odds)

        ParimatchScraper._check_data_integrity(match_titles, bet_titles, odds)

        for i in range(len(match_titles)):
            bets[match_titles[i]] = {}
            for j in range(len(bet_titles)):
                bets[match_titles[i]][bet_titles[j]] = odds[i][j]

        return bets

    @staticmethod
    def _get_odds(soup, other_titles_count):
        """
        Scraps all odds found in the soup

        :param soup: parsed document created from the championship url's html
        :type soup: BeautifulSoup
        :param other_titles_count: count of titles on the website that don't
        contain information about odds such as '№', 'Event', 'Date'
        :type other_titles_count: int
        :return: list of lists with match odds
        :rtype: list
        """
        odds = []
        tags = []

        tags_temp = soup.find_all(class_='bk')
        for tag in tags_temp:
            if 'props' not in tag.parent['class']:
                tags.append(tag)

        for tag in tags:
            tag = tag.next_element
            for i in range(other_titles_count):
                tag = tag.find_next_sibling()
            bet_tags = tag.find_next_siblings()

            match_odds = []
            for bet_tag in bet_tags:
                match_odds += ParimatchScraper._get_packed_odds(bet_tag, 'a',
                                                                'b')

            odds.append(match_odds)

        return odds

    @staticmethod
    def _get_match_titles(soup):
        """
        Scraps all match titles found in the soup

        :param soup: parsed document created from the championship url's html
        :type soup: BeautifulSoup
        :return: list of match titles
        :rtype: list
        """
        match_titles = []
        tags = soup.find_all(class_='l')
        for tag in tags:
            br_tag = tag.find('br')
            first_team = ParimatchSyntaxFormatter.format_team_name(
                br_tag.previous_element)
            second_team = ParimatchSyntaxFormatter.format_team_name(
                br_tag.next_element)
            match_title = first_team + ' - ' + second_team
            match_titles.append(match_title)

        return match_titles

    @staticmethod
    def _get_bet_titles(soup):
        """
        Scraps all bet titles found in the soup

        :param soup: parsed document created from the championship url's html
        :type soup: BeautifulSoup
        :return: list of bet titles
        :rtype: list
        """
        bet_titles = []
        tag = soup.find(class_='processed')
        try:
            event_tag = tag.find(string='Event').parent
        except AttributeError:
            raise ScrapingUnsuccessfulException("Failed to render website...")
        bet_title_tags = event_tag.find_next_siblings()
        for bet_title_tag in bet_title_tags:
            try:
                bet_titles.append(bet_title_tag['title'])
            except KeyError:
                bet_titles.append(bet_title_tag.text)

        return bet_titles

    @staticmethod
    def _get_other_titles_count(soup):
        """
        Scraps count of titles on the website that don't contain information
        about odds

        :param soup: parsed document created from the championship url's html
        :type soup: BeautifulSoup
        :return: count of titles on the website that don't
        contain information about odds such as '№', 'Event', 'Date'
        :rtype: int
        """
        tag = soup.find(class_='processed')
        event_tag = tag.find(string='Event').parent
        other_titles_count = len(event_tag.find_previous_siblings())
        return other_titles_count

    @staticmethod
    def _get_packed_odds(root_tag, *tags_to_find):
        """
        Scraps odds contained in the root_tag from inner tags packing them
        together in list if there are more than one text fields found

        :param root_tag:
        :type root_tag: Tag
        :param tags_to_find: tags that will be searched for inside of the
        root_tag; odds from them will be scraped and put into the resulting list
        :return: list that contains odds found inside tags_to_find(they are
        packed into another list if there is more than one of them);
        :rtype: list

        :Example:

        odds = [2.55]
        odds = [[2.55, 1.47]]
        """
        odds = []
        for tag in tags_to_find:
            if root_tag.find(tag):
                found_tags = root_tag.find_all(tag)
                if len(found_tags) > 1:
                    odds_list = []
                    for found_tag in found_tags:
                        odds_list.append(found_tag.text)
                    odds.append(odds_list)
                else:
                    odds.append(found_tags[0].text)

        return odds

    @staticmethod
    def _check_data_integrity(match_titles, bet_titles, odds):
        """
        Checks if all the odds were found for the match, raises
        OddsNotFoundError if not

        :param match_titles: list of match titles
        :param bet_titles: list of bet titles
        :param odds: odds list
        :raises OddsNotFoundError:
        """
        for o in odds:
            if len(bet_titles) != len(o):
                raise OddsNotFoundError('Can\'t find odds for one or more bet '
                                        'titles')
        if len(odds) != len(match_titles):
            raise OddsNotFoundError('Can\'t find odds for one or more match '
                                    'titles')


# urls = ParimatchScraper.get_championships_urls()

url1 = 'https://www.parimatch.com/en/sport/kibersport/counter-strike-esea-eu-advanced-s33'
url2 = 'https://www.parimatch.com/en/sport/kibersport/counter-strike-blast-premier-spring'
url3 = 'https://www.parimatch.com/en/sport/kibersport/dota-2-parimatch-league-s2'
url4 = 'https://www.parimatch.com/en/sport/kibersport/liga-legend-lck'
url5 = 'https://www.parimatch.com/en/sport/volejjbol/liga-chempionov'

bets = ParimatchScraper.get_bets(url2)
pprint(bets)
