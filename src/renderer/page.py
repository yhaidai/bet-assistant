import os
import time
from threading import Thread

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from exceptions.RendererTimeoutException import RendererTimeoutException


class Page:
    """
    Class that represents rendered web page
    """
    _chrome_options = webdriver.ChromeOptions()
    _chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # _chrome_options.add_argument("--headless")
    _chrome_options.add_argument("--disable-dev-shm-usage")
    _chrome_options.add_argument("--no-sandbox")
    _chrome_options.add_argument("--incognito")
    _chrome_options.add_argument("--window-size=1920,1080")
    _chrome_options.add_argument("--disable-extensions")
    _chrome_options.add_argument("--dns-prefetch-disable")
    _chrome_options.add_argument("--disable-gpu")
    _chrome_options.add_argument("--disable-browser-side-navigation")
    _chrome_options.add_argument("--disable-infobars")
    _chrome_options.add_argument("enable-automation")
    _chrome_options.add_argument("start-maximized")
    # _chrome_options.add_argument(
    #     '--user-agent=""Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #     'Chrome/74.0.3729.157 Safari/537.36""'
    # )
    try:
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=_chrome_options)
    except Exception:
        driver = webdriver.Chrome(executable_path='../renderer/chromedriver_win32/chromedriver.exe',
                                  chrome_options=_chrome_options)

    def __init__(self, url):
        """
        Renders web page located at given url

        :param url: url of the web page that needs to be rendered
        :type url: str
        """
        self.url = url
        try:
            Page.driver.get(url)
        except TimeoutException as e:
            raise RendererTimeoutException(message=e.msg)
        self.html = Page.driver.page_source

    @staticmethod
    def change_driver():
        """
        Change chromedriver to a new instance
        """
        try:
            Page.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                           chrome_options=Page._chrome_options)
        except Exception:
            Page.driver = webdriver.Chrome(executable_path='../renderer/chromedriver_win32/chromedriver.exe',
                                           chrome_options=Page._chrome_options)

    @staticmethod
    def click(element):
        """
        Clicks on the given element even if its not visible in the browser window

        :param element: element to click on
        :type element: selenium.WebElement
        """
        Page.driver.execute_script("arguments[0].click();", element)
