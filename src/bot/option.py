from util import get_arbitrage_bets_xlsx_filename


class Option:
    id = 0

    def __init__(self, text=None, prompt=None, attach_arbitrage_bets=False, action=None, *args):
        self.text = text
        self.prompt = prompt
        self.parent = None
        self.children = []
        self.filename = None
        if attach_arbitrage_bets:
            self.filename = get_arbitrage_bets_xlsx_filename(text)
        self.action = action
        self.action_args = args
        self.id = Option.id
        Option.id += 1

    def __contains__(self, item):
        for option in self.children:
            if option.text == item:
                return True
        return False

    def __getitem__(self, item):
        for option in self.children:
            if option.text == item:
                return option
        raise KeyError

    def __repr__(self):
        return str(self.text)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        return self

    def add_children(self, *args):
        for child in args:
            self.add_child(child)
        return self

    def is_leaf(self):
        return not bool(self.children)

    def make_action(self):
        if self.action:
            return self.action(*self.action_args)
