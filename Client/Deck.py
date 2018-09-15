from Card import *
class Deck:
    def __init__(self, deckname, deck_list):
        self.deck_list = deck_list
        self.deck_name = deckname

    def add_card(self, cardname):
        self.deck_list.append(Card(cardname))

    def remove_card(self):
        pass

    def save(self):
        pass

    def delete(self):
        pass
