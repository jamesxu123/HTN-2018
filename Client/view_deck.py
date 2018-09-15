from pygame import *
import threading
import pickle
from client import Deck, Card


def draw_deck(area, deck):
    total = len(deck.deck_list)
    width = 120
    for card in deck.deck_list:
        has_img = card.img
        if card.img == None:
            card.downloadIm()
    x, y, w, h = area

    row_length = w // (width + 30)
    num_rows = total // (row_length + 30)
    remaining = total - row_length * num_rows
    sample_height = 120 / width * deck.deck_list[0].img.get_height()

    surface = Surface((w, (sample_height+30) * num_rows))

    current_row = 0
    current_col = 0

    for card in deck.deck_list:
        img = card.img
        height = img.get_height()
        width = img.get_width()
        scaled = transform.smoothscale(img, (120, 120 / width * height))

        if current_col == 0:
            if current_row == 0:
                surface.blit(scaled, (current_col, current_row))
            else:
                surface.blit(scaled, (current_col, current_row * height + 15))
        else:
            surface.blit(scaled, (current_col * height + 15, current_row * height + 15))

        current_col += 1
        if current_col % row_length == 0:
            current_col = 0
            current_row += 1

    return surface


if __name__ == '__main__':
    cards = pickle.load(open('CardList.p', 'rb'))
    deck = Deck("deck1", [])
    for i in range(60):
        card = Card(list(cards.keys())[i], cards)
        deck.add_card(card)
    while True:
        draw_deck(Rect(0,0,800,600), deck)
        display.flip()
