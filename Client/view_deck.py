from pygame import *
import threading
from client import Deck, Card

screen = display.set_mode((800, 600), RESIZABLE)


def draw_deck(area, deck):
    total = len(deck.deck_list)
    width = 120
    for card in deck.deck_list:
        has_img = card.img
        if not has_img:
            threading.Thread(target=card.downloadIm()).start()
    x, y, w, h = area

    row_length = w // (width + 30)
    num_rows = total // (row_length + 30)
    remaining = total - row_length * num_rows
    sample_height = 120 / width * deck.deck_list[0].get_height()
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