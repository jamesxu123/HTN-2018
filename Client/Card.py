import requests
import os
import pygame
class Card:
    def __init__(self, cardname, card_DataB):
        self.cname = cardname
        if "type" in card_DataB[cardname]:
            self.type = card_DataB[cardname]["type"]
        if "Creature" in self.type:
            self.power = card_DataB[cardname]["power"]
            self.toughness = card_DataB[cardname]["toughness"]
            self.cmc = card_DataB[cardname]["cmc"]
        if "colors" in card_DataB[cardname]:
            self.colors = card_DataB[cardname]["colors"]
        if "manaCost" in card_DataB[cardname]:
            self.manaCost = card_DataB[cardname]["manaCost"]
        if "text" in card_DataB[cardname]:
            self.text = card_DataB[cardname]["text"]
            self.alt = False
        if card_DataB[cardname]["layout"] == "double-faced":
            if card_DataB[cardname]["names"][0] == cardname:
                self.alt = card_DataB[cardname]["names"][1]
            else:
                self.alt = card_DataB[cardname]["names"][0]
        self.img = None
        if "imageUrl" in card_DataB[cardname]:
            self.imgUrl = card_DataB[cardname]["imageUrl"]

    def downloadIm(self):
        if (not os.path.exists("Card Images/" + self.cname + ".jpg")):
            image_url = self.imgUrl
            img_data = requests.get(image_url).content
            with open("Card Images/" + self.cname + '.jpg', 'wb') as handler:
                handler.write(img_data)
            self.img = pygame.image.load("Card Images/" + self.cname + ".jpg", "wb")