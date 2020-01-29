class OddsNotFoundError(Exception):
    def __int__(self, message):
        self.message = message
