# HTN hack; Noor Nasri, James Xu, Anish Aagarwal

################ Importing modules #########################
import functools
import glob
import json
import os
import pickle
import socket
import time

import pygame
import requests

pygame.font.init()


################ Public Classes #########################
# Deck class to allow for deck editing
class Deck:
    def __init__(self, deckname, deckl):
        self.deck_list = deckl
        self.dname = deckname

    def add_card(self, cardname, card_DataB):
        self.deck_list.append(Card(cardname, card_DataB))

    def remove_card(self, card_name):
        found = False
        for card in self.deck_list:
            if card.cname == card_name:
                found = True
                break
        if found:
            del self.deck_list[card]


    def save(self, user):
        user.curDecks[self.dname] = self.deck_list

    def delete(self):
        pass


# User class for keeping track of profile things
class User:
    def __init__(self):
        self.name = "None"
        self.win = 0
        self.loss = 0
        self.curDecks = {}
        self.token = None

    def make_user(self, username, password, req):  # "sign_in" "create_user"
        payloads = {'username': username, 'password': password}

        items = requests.post(base_url + req, data=json.dumps(payloads), headers={'content-type': 'application/json'})
        ret_item = items.json()
        if ret_item["status"] == 200:
            global current_screen
            if req == "create_user":
                print("Account created")
                self.make_user(username,password,"sign_in")
            else:
                self.name = username
                self.token = ret_item["token"]
                self.get_data()
                current_screen = "Deck Building"
                print("Account log in") 
            return True
        return False

    def get_data(self):  # Once you log in
        payloads = {'username': self.name, 'token': self.token}
        items = requests.post(base_url + "get_stats", data=json.dumps(payloads),
                              headers={'content-type': 'application/json'})
        ret_item = items.json()
        if ret_item["status"] == 200:
            stats = ret_item["data"]
            self.win = stats["wins"]
            self.loss = stats["losses"]

        payloads = {'username': self.name, 'token': self.token}
        items = requests.post(base_url + "get_decks", data=json.dumps(payloads),
                              headers={'content-type': 'application/json'})
        ret_item = items.json()
        if ret_item["status"] == 200:
            deck = ret_item["data"]
            for deckname in deck:
                self.curDecks[deckname] = Deck(deckname, deck[deckname])


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
        
        if "CardImages//"+self.cname+".jpg" in existingImages:
            self.img = pygame.image.load("Card Name/" +self.cname+".jpg")
            print(self.img)
        card_DataB[cardname] 
        

    def downloadIm(self):
            if(self.img==None):
                image_url = self.imgUrl
                img_data = requests.get(image_url).content
                with open("Card Images/" + self.cname + '.jpg',"rb") as handler:
                    handler.write(img_data)
                self.img = pygame.image.load("Card Images/" + self.cname + ".jpg")
                print(self.img)

    def __hash__(self):
        return hash(self.cname) ^ hash(self.text) ^ hash(self.imgUrl)


################ Public functions #########################
def transparent_rect(x, y, b, h, alpha,colour = (0,0,0)):
    transparent_screen = pygame.Surface((b, h))
    transparent_screen.fill(colour)
    transparent_screen.set_alpha(alpha)
    return screen.blit(transparent_screen, (x, y))


def text_with_outline(text, myfont, col_main, col_outline, x, y, outline_width, scale_needed):
    main_text = myfont.render(text, True, col_main)  # The main colour text
    outline_text = myfont.render(text, True, col_outline)  # The text rendered with the outline colour

    # Blit the outline text 4 times around the main text, then blit the main text
    stuff = [[int(e * size_ratio) if scale_needed else e for e in [x, y]] for a in range(5)]
    extra = [[outline_width, 0], [outline_width * -1, 0], [0, outline_width], [0, outline_width * -1]]
    for a in range(4):
        stuff[a][0] += extra[a][0]
        stuff[a][1] += extra[a][1]
    for outlinePos in stuff[:-1]:
        screen.blit(outline_text, outlinePos)
    screen.blit(main_text, stuff[-1])


@functools.lru_cache(maxsize=None)
def font_size(font, text, max_width, max_height, size):  # Recurssion with memoization
    myfont = pygame.font.SysFont(font, size)
    x, y = pygame.font.Font.size(myfont, text)
    if x < max_width and y < max_height or size < 4:
        return [size, x, y, myfont]
    return font_size(font, text, max_width, max_height, size - 3)


def set_deck(username, token, deck_name, deck_data):
    payload = {'username': username, 'token': token, 'deck_name': deck_name, 'deck_data': deck_data}
    items = requests.post(base_url + "set_decks", data=json.dumps(payload))
    ret_item = json.loads(items)
    return ret_item["status"] == 200


def del_deck(username, token, deck_name):
    payload = {'username': username, 'token': token, 'deck_name': deck_name}
    items = requests.post(base_url + "del_deck", data=json.dumps(payload))
    ret_item = json.loads(items)
    return ret_item["status"] == 200


def search_card(key_note):
    list_good = []
    for key in card_database:
        if key_note.lower() in key.lower():
            list_good.append(card_database[key])
    return list_good

def get_cards():
    print('GETTING')
    items = requests.get(base_url + "get_cards")
    ret_item = items.json()
    print("Request returned")
    return ret_item["data"]


    
################ Game Variables #########################
base_url = "https://mtg.jamesxu.ca/"
existingImages = glob.glob("Card Images/*")
if 'CardList.p' in glob.glob('*.p'):
    card_database = pickle.load(open('CardList.p', 'rb'))
else:
    file = open('CardList.p', 'wb')
    card_database = get_cards()
    pickle.dump(card_database, file)
    file.close()

for card in card_database:
    card_database[card] = Card(card, card_database)

current_screen = "Login Menu"
current_selection = "Nil"
typing = False
typing_reference = None
user_item = User()

cur_background = 0
bck_direction = 1

menu_specifications = {"Login Menu": {"Username": "Username", "Password": "Password"},
                       'Main Menu': {},
                       'Deck Building': {"Search":"Search", "Items":[], "Current_Scroll":0}
                       }

# Setting up pygame
original_screen = [1000,625]
screen = pygame.display.set_mode(original_screen, pygame.RESIZABLE)

pygame.display.set_caption("HTN Program")
size_ratio = 1

original_images = {}
images_database = {}

path_way = os.path.dirname(os.path.realpath(__file__))  # Directory to the python file
for image in os.listdir(path_way + "/Images"):  # Loading images
    save_path = "Images/" + image
    if image[-3:] == "jpg" or image[-3:] == "png":
        curImg = pygame.image.load(save_path)
        sizes = list(map(int, image[image.rfind("_") + 1:image.rfind(".")].split("x")))
        original_images[image[:image.rfind("_")]] = [curImg, sizes[0], sizes[1]]

################ Connecting socket #########################
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = "localhost"
port = 224
# server.connect((host_ip, port))
images_database = {}


def setup():
    global images_database
    for image in original_images:
        im = original_images[image][:]
        try:
            images_database[image] = pygame.transform.smoothscale(im[0],
                                                                  (int(size_ratio * im[1]), int(size_ratio * im[2])))
        except:
            images_database[image] = pygame.transform.scale(im[0], (int(size_ratio * im[1]), int(size_ratio * im[2])))


setup()
################ Game loop #########################
running = True
start = time.time()
first = True

while running:
    clicked = False
    scrolled = 0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # They clicked with the left click
            clicked = True
        elif event.type == pygame.KEYDOWN and typing:
            if event.key == pygame.K_BACKSPACE:
                if len(typing_reference[current_selection]) > 0:
                    typing_reference[current_selection] = typing_reference[current_selection][:-1]

            elif event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:  # Remove it
                if current_selection == "Search":
                    typing_reference["Items"] = search_card(typing_reference["Search"])
                else:
                    typing = False
                    typing_reference = None
                    current_selection = "Nil"

            elif event.key < 256:  # Add new char
                typing_reference[current_selection] += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button==5: #They scrolled downwards
            scrolled = 1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button==4: #They scrolled upwards
            scrolled = -1
            
        elif event.type == pygame.VIDEORESIZE:
            print('resize')
            x, y = event.w, event.h
            requested_size = [x, y]
            ratio_wanted = original_screen[0] / original_screen[1]
            ratio_requested = requested_size[0] / requested_size[1]

            if ratio_requested > ratio_wanted + 0.01:
                requested_size[0] = int(requested_size[1] * ratio_wanted)
            elif ratio_requested < ratio_wanted - 0.01:
                requested_size[1] = int(requested_size[0] / ratio_wanted)

            size_ratio = requested_size[1] / original_screen[1]
            screen = pygame.display.set_mode(requested_size, pygame.RESIZABLE)

            # Resize images
            images_database = {}
            for image in original_images:
                im = original_images[image][:]
                try:
                    images_database[image] = pygame.transform.smoothscale(im[0], (
                        int(size_ratio * im[1]), int(size_ratio * im[2])))
                except:
                    images_database[image] = pygame.transform.scale(im[0],
                                                                    (int(size_ratio * im[1]), int(size_ratio * im[2])))

    if clicked and typing:  # Remove it
        typing = False
        typing_reference = None
        current_selection = "Nil"

    cur = time.time()
    mx, my = pygame.mouse.get_pos()

    sc_params = menu_specifications[current_screen]
    screen.fill((255, 255, 255))
    cur_background += bck_direction
    if cur_background == 47 or cur_background == 0:
        bck_direction *= -1
    if current_screen == "Login Menu":
        screen.blit(images_database["IntroGif%i" % (cur_background)], [int(e * size_ratio) for e in [0, 0]])
        for i in range(2):
            im_name, im_pos = ["Sign Up", "Sign In"][i], [[800, 510], [800, 560]][i]
            im_pos = [int(e * size_ratio) for e in im_pos]
            item = screen.blit(images_database[im_name], im_pos)
            if item.collidepoint(mx, my) and clicked:  # They signed up or in!
                user_item.make_user(sc_params["Username"], sc_params["Password"], ["create_user", "sign_in"][i])

        # Username and password bars
        buttons = [
            transparent_rect(int(375 * size_ratio), int(510 * size_ratio), int(250 * size_ratio), int(40 * size_ratio),
                             120),
            transparent_rect(int(375 * size_ratio), int(575 * size_ratio), int(250 * size_ratio), int(40 * size_ratio),
                             120)]

        for a in range(2):
            if buttons[a].collidepoint(mx, my) and clicked:
                current_selection = ["Username", "Password"][a]
                sc_params[current_selection] = ""
                typing = True
                typing_reference = sc_params

        largest_size1, x_taken1, y_taken, myfont1 = font_size("timesnewroman", sc_params["Username"],
                                                              int(250 * size_ratio), int(40 * size_ratio), 60)
        largest_size2, x_taken2, y_taken, myfont2 = font_size("timesnewroman", sc_params["Password"],
                                                              int(250 * size_ratio), int(40 * size_ratio), 60)

        mysize = largest_size1 < largest_size2 and largest_size1 or largest_size2
        myfont = pygame.font.SysFont("timesnewroman", mysize)  # Make for both

        x_taken = pygame.font.Font.size(myfont, sc_params["Username"])[0]
        text_with_outline(
            sc_params["Username"] + (current_selection == "Username" and cur_background // 8 % 2 == 0 and '|' or ""),
            myfont, (255, 255, 255), (0, 0, 0), int(500 * size_ratio) - x_taken // 2, int(512 * size_ratio), 1, False)

        x_taken = pygame.font.Font.size(myfont, sc_params["Password"])[0]
        text_with_outline(sc_params["Password"] + (current_selection == "Password" and cur_background // 8 % 2 == 0 and '|' or ""),
            myfont, (255, 255, 255), (0, 0, 0), int(500 * size_ratio) - x_taken // 2, int(577 * size_ratio), 1, False)

    elif current_screen == "Deck Building":
        screen.blit(images_database["DeckBck"], (0,0))
        side_bar = transparent_rect(0, 0, int(200 * size_ratio), int(625 * size_ratio),60)
        search_bar = transparent_rect(int(25*size_ratio), int(20*size_ratio), int(150 * size_ratio), int(40 * size_ratio),100)

        if search_bar.collidepoint((mx,my)):
            if clicked:
                current_selection = "Search"
                sc_params["Search"] = ""
                typing = True
                typing_reference = sc_params
        elif side_bar.collidepoint((mx,my)):
            sc_params["Current_Scroll"] = min(max(sc_params["Current_Scroll"] + scrolled,0), len(sc_params["Items"]))
            
            
        largest_size, x_taken, y_taken, myfont = font_size("timesnewroman", sc_params["Search"],
                                                              int(150 * size_ratio), int(40 * size_ratio), 60)
        text_with_outline(sc_params["Search"] + (current_selection == "Search" and cur_background // 8 % 2 == 0 and '|' or ""),
            myfont, (255, 255, 255), (0, 0, 0), int(100 * size_ratio) - x_taken // 2, int(21 * size_ratio), 1, False)

        #Font size for all 0-9 cards
        largest_size, x_taken, y_taken, myfont = font_size("timesnewroman", sc_params["Search"],
                                                              int(150 * size_ratio), int(40 * size_ratio), 60)
        for a in range(sc_params["Current_Scroll"], sc_params["Current_Scroll"]+9):
            if a >= len(sc_params["Items"]):
                break
            card_object = sc_params["Items"][a]
            card_bar = transparent_rect(0, int((a- sc_params["Current_Scroll"]+1)*100*size_ratio), int(200 * size_ratio), int(100 * size_ratio),20)
            if card_bar.collidepoint((mx,my)):
                transparent_rect(0, int((a- sc_params["Current_Scroll"]+1)*100*size_ratio), int(200 * size_ratio), int(100 * size_ratio),50)
                #Call card function
            main_text = myfont.render(card_object.cname, True, (255,255,255))
            screen.blit(main_text, (0, int((a- sc_params["Current_Scroll"]+1)*100*size_ratio)))
            
        transparent_rect(int(350 * size_ratio), int(25 * size_ratio), int(350 * size_ratio), int(75 * size_ratio), 120)
        transparent_rect(int(250 * size_ratio), int(175 * size_ratio), int(550 * size_ratio), int(400 * size_ratio), 90)
        transparent_rect(int(850 * size_ratio), int(150 * size_ratio), int(150 * size_ratio), int(300 * size_ratio), 90)
        
        
        

    pygame.display.flip()
    time.sleep(0.04)
pygame.quit()
