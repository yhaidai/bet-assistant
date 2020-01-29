import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage


class Page(QWebEnginePage):
    """
    Class that represents rendered web page

    :param app: QApplication needed to render the web page
    :type app: QApplication
    :param html: text string that contains all the html code from the web
    page after rendering javascript
    :type html: str
    """
    app = QApplication(sys.argv)

    def __init__(self, url):
        """
        Loads web page and executes _on_load_finished when the loading is
        finished

        :param url: url of the web page that needs to be rendered
        :type url: str
        """
        QWebEnginePage.__init__(self)
        self.html = ''
        self.loadFinished.connect(self._on_load_finished)
        self.load(QUrl(url))
        Page.app.exec_()

    def _on_load_finished(self):
        """Sets html field of the class after the rendering is finished"""
        # self.toPlainText(self._callable)
        self.toHtml(self._callable)

    def _callable(self, html_str):
        """
        Called by toHtml() method to set html field of the class;
        quits the app after
        """
        self.html = html_str
        Page.app.quit()
