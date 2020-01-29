class ScrapingUnsuccessfulException(Exception):
    """
    Class that represents an exception that indicates that web scraping was
    unsuccessful

    :param message: message that will be shown when an exception is raised
    :type message: str
    """
    def __init__(self, message):
        self.message = message
