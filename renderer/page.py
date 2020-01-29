import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage


class Page(QWebEnginePage):
    app = QApplication(sys.argv)

    def __init__(self, url):
        QWebEnginePage.__init__(self)
        self.html = ''
        self.loadFinished.connect(self._on_load_finished)
        self.load(QUrl(url))
        Page.app.exec_()

    def _on_load_finished(self):
        # self.toPlainText(self._callable)
        self.toHtml(self._callable)

    def _callable(self, html_str):
        self.html = html_str
        Page.app.quit()
