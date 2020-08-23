import os

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait


class Renderer(webdriver.Chrome):
    _chrome_options = webdriver.ChromeOptions()
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

    def __init__(self):
        super().__init__(executable_path='../scrapers/renderer/chromedriver_win32/chromedriver.exe',
                         chrome_options=self._chrome_options)
        self.wait = WebDriverWait(self, 3)

    def click(self, web_element: WebElement):
        self.execute_script("arguments[0].click();", web_element)
