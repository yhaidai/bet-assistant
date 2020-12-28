from menu import Menu


class User:
    def __init__(self, user_id: str, subscriptions=None, last_menu_option_id=0):
        if subscriptions is None:
            subscriptions = []
        self.id = user_id
        self.subscriptions = subscriptions
        self.menu = Menu(self)
        self.menu.set_current_option(last_menu_option_id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f'User(id={self.id}, subscriptions={self.subscriptions}, last menu option id=' \
               f'{self.menu.current_option.id})'

    def subscribe(self, sport_name):
        if sport_name not in self.subscriptions:
            self.subscriptions.append(sport_name)
            self.subscriptions.sort()

    def unsubscribe(self, sport_name):
        if sport_name in self.subscriptions:
            self.subscriptions.remove(sport_name)
