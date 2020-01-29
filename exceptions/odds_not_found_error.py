class OddsNotFoundError(Exception):
    """
    Class that represents an exception that indicates that some of the odds were
    not found during web scraping

    :param message: message that will be shown when an exception is raised
    :type message: str
    """
    def __int__(self, message):
        self.message = message
