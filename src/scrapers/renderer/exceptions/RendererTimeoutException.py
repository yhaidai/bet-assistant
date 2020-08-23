from selenium.common.exceptions import TimeoutException


class RendererTimeoutException(TimeoutException):
    def __init__(self, message):
        super().__init__(message)
