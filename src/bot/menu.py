from constants import SPORT_SHORT_NAMES_TO_FULL
from option import Option


class Menu:
    __SPORT_NAMES = ()
    __ROOT_OPTION_TEXT = 'Root option'
    __ACTION_SELECTION_PROMPT = '*Choose action*'
    __SPORT_SELECTION_PROMPT = '*Choose kind of sport*'
    __SHOW_SUBSCRIPTIONS_PROMPT = 'You are currently subscribed to:\n'

    def __init__(self, user, root=None, go_back_option_text='Go Back'):
        self.user = user
        self.go_back_option_text = go_back_option_text
        if root is None:
            root = self.__get_default_tree()
        self.root = root
        self.current_option = self.root

    def __get_default_tree(self):
        Option.id = 0

        root = Option(Menu.__ROOT_OPTION_TEXT, Menu.__ACTION_SELECTION_PROMPT)
        root.add_children(
            Option('Arbitrage bets', Menu.__SPORT_SELECTION_PROMPT).add_children(
                Option('Counter-Strike: Global Offensive', '*Counter-Strike: Global Offensive arbitrage bets*', True),
                Option('Dota 2', '*Dota 2 arbitrage bets*', True),
                Option('League of Legends', '*League of Legends arbitrage bets*', True),
                Option('Football', '*Football arbitrage bets*', True),
                Option(self.go_back_option_text, Menu.__SPORT_SELECTION_PROMPT)
            ),
            Option('Subscribe', Menu.__SPORT_SELECTION_PROMPT).add_children(
                Option('Counter-Strike: Global Offensive',
                       '*Successfully subscribed to Counter-Strike: Global Offensive*', False,
                       self.user.subscribe, 'csgo'),
                Option('Dota 2', '*Successfully subscribed to Dota 2*', False,
                       self.user.subscribe, 'dota'),
                Option('League of Legends', '*Successfully subscribed to League of Legends*', False,
                       self.user.subscribe, 'lol'),
                Option('Football', '*Successfully subscribed to Football*', False,
                       self.user.subscribe, 'football'),
                Option(self.go_back_option_text, Menu.__SPORT_SELECTION_PROMPT)
            ),
            Option('Unsubscribe', Menu.__SPORT_SELECTION_PROMPT).add_children(
                Option('Counter-Strike: Global Offensive',
                       '*Successfully unsubscribed from Counter-Strike: Global Offensive*', False,
                       self.user.unsubscribe, 'csgo'),
                Option('Dota 2', '*Successfully unsubscribed from Dota 2*', False,
                       self.user.unsubscribe, 'dota'),
                Option('League of Legends', '*Successfully unsubscribed from League of Legends*', False,
                       self.user.unsubscribe, 'lol'),
                Option('Football', '*Successfully unsubscribed from Football*', False,
                       self.user.unsubscribe, 'football'),
                Option(self.go_back_option_text, Menu.__SPORT_SELECTION_PROMPT)
            ),
            Option('Show my subscriptions', Menu.__SHOW_SUBSCRIPTIONS_PROMPT, False,
                   lambda user: '*' + '\n'.join([SPORT_SHORT_NAMES_TO_FULL[sub] for sub in user.subscriptions]) + '*',
                   self.user)
        )
        return root

    def choose(self, option):
        if option == self.go_back_option_text:  # step back
            if self.current_option.parent is not None:
                self.current_option = self.current_option.parent
        else:
            if option in self.current_option:  # step forward
                self.current_option = self.current_option[option]
            else:  # reset if option is unknown
                self.current_option = self.root

        return self.current_option.make_action()

    def get_current_options(self):
        return [child.text for child in self.current_option.children]

    def set_current_option(self, option_id: int, root=None):
        if root is None:
            root = self.root

        if root.id == option_id:
            self.current_option = root
        else:
            for option in root.children:
                self.set_current_option(option_id, option)


if __name__ == '__main__':
    m = Menu()
    m.choose('Arbitrage bets')
    m.choose('Dota 2')
    m.set_current_option(1)
    # m.choose('Go Back')
    print(m.current_option.id)
