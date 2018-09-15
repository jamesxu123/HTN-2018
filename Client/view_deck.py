from pygame import *
import threading
import pickle
from client import Deck, Card

def download_deck(deck):
    for card in deck.deck_list:
        has_img = card.img
        if card.img is None:
            threading.Thread(target=card.downloadIm).start()

def draw_deck(area, deck):
    total = len(deck.deck_list)
    width = 120

    threading.Thread(target=download_deck, args=(deck,)).start()

    x, y, w, h = area
    row_length = w // (width + 12)
    num_rows = total // (row_length + 12)
    remaining = total - row_length * num_rows
    surface = Surface((w, (190 + 12) * (num_rows + 1 + int(remaining > 0))))

    current_row = 0
    current_col = 0

    for card in deck.deck_list:
        img = card.img
        if img is None:
            continue
        scaled = transform.smoothscale(img, (120, 190))

        height = scaled.get_height()
        width = scaled.get_width()

        # if current_col == 0:
        #     if current_row == 0:
        #         surface.blit(scaled, (current_col, current_row))
        #     else:
        #         surface.blit(scaled, (current_col, current_row * height + 7))
        # else:
        surface.blit(scaled, (current_col * width + 12 * current_col, current_row * height + 12 * current_row))

        current_col += 1
        if current_col == row_length:
            current_col = 0
            current_row += 1

    return surface


if __name__ == '__main__':

    init()
    cards = pickle.load(open('CardList.p', 'rb'))
    deck = Deck("deck1", [])
    for i in range(25):
        card = Card(list(cards.keys())[i], cards)
        deck.add_card(card)

    screen = display.set_mode((800, 600), RESIZABLE)
    running = True
    offset = 0
    while running:
        screen.fill(0)
        for e in event.get():
            if e.type == QUIT:
                running = False
            if e.type == VIDEORESIZE:
                x, y = e.w, e.h
                screen = display.set_mode((x, y), RESIZABLE)
            if e.type == MOUSEBUTTONDOWN and e.button == 4:
                offset += 5
            if e.type == MOUSEBUTTONDOWN and e.button == 5:
                offset -= 5
        screen.blit(draw_deck(Rect(0, 0, screen.get_width(), screen.get_height()), deck), (0, 0 + offset))
        display.flip()
