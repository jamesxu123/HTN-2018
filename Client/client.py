#HTN hack; Noor Nasri, James Xu, Anish Aagarwal

################ Importing modules #########################
import socket, pickle
import time
import requests
import json
import random
import threading
import pygame
import glob
import os
import functools

pygame.font.init()
################ Public Classes #########################
#Deck class to allow for deck editing
#Deck class to allow for deck editing
class Deck:
    def __init__(self,deckname, deckl):
        self.deck_list = deckl
        self.dname = deckname
    
    def add_card(self,cardname,card_DataB):
        self.deck_list.append(Card(cardname,card_DataB))

    def remove_card():
        pass
    
    def save():
        pass

    def delete():
        pass

#User class for keeping track of profile things
class User:
    def __init__(self):
        self.name = "None"
        self.win = 0
        self.loss = 0
        self.curDecks = {}
        self.token = None

    def make_user(self,username, password, req): #"sign_in" "create_user"
        payloads = {'username':username, 'password':password}
        
        items = requests.post(base_url + req, data = json.dumps(payloads), headers = {'content-type':'application/json'})
        ret_item = items.json()
        if ret_item["status"] == 200:
            self.token = ret_item["token"]
            self.name = username
            self.get_data()
            global current_screen
            current_screen = "Main Menu"
            print("Account success")
            return True
        return False
    
  
    def get_data(self): #Once you log in
        payloads = {'username':self.name, 'token':self.token}
        items = requests.post(base_url + "get_stats", data = json.dumps(payloads), headers = {'content-type':'application/json'})
        ret_item = items.json()
        if ret_item["status"] == 200:
            stats =  ret_item["data"]
            self.win = stats["wins"]
            self.loss = stats["losses"]
            
            
        payloads = {'username':self.name, 'token':self.token}
        items = requests.post(base_url + "get_decks", data = json.dumps(payloads), headers = {'content-type':'application/json'})
        ret_item = items.json()
        if ret_item["status"] == 200:
            deck = ret_item["data"]
            for deckname in deck:
                self.curDecks[deckname] = Deck(deckname, deck[deckname])
    


class Card:
    def __init__(self,cardname,card_DataB):
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
        if  "text" in card_DataB[cardname]:
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
        if (not os.path.exists("Card Images/"+self.cname+".jpg")):
            image_url = self.imgUrl
            img_data = requests.get(image_url).content
            with open("Card Images/"+self.cname+'.jpg', 'wb') as handler:
                handler.write(img_data)
            self.img = pygame.image.load("Card Images/"+self.cname+".jpg","wb")
        
            

################ Public functions #########################
def transparent_rect(x,y,b,h, alpha):
    transparent_screen = pygame.Surface((b,h))  
    transparent_screen.set_alpha(alpha)    
    return screen.blit(transparent_screen, (x,y))
        
def text_with_outline(text,myfont,col_main, col_outline, x, y, outline_width, scale_needed): 
    main_text = myfont.render(text, True, col_main) #The main colour text
    outline_text = myfont.render(text, True, col_outline) #The text rendered with the outline colour

    #Blit the outline text 4 times around the main text, then blit the main text
    stuff = [[int(e*size_ratio) if scale_needed else e for e in [x,y]] for a in range(5)]
    extra = [[outline_width,0],[outline_width*-1,0],[0,outline_width],[0,outline_width*-1]]
    for a in range(4):
        stuff[a][0] += extra[a][0]
        stuff[a][1] += extra[a][1]
    for outlinePos in stuff[:-1]:
        screen.blit(outline_text,outlinePos)
    screen.blit(main_text,stuff[-1])

@functools.lru_cache(maxsize=None)
def font_size(font,text,max_width,max_height,size):#Recurssion with memoization
    myfont = pygame.font.SysFont(font, size)
    x,y = pygame.font.Font.size(myfont,text) 
    if x<max_width and y<max_height or size<4:
        return [size,x,y,myfont]
    return font_size(font,text,max_width,max_height,size-3)

def set_deck(username, token, deck_name, deck_data):
    payload = {'username':username, 'token':token, 'deck_name':deck_name, 'deck_data':deck_data}
    items = requests.post(base_url + "set_decks", data = json.dumps(payloads))
    ret_item = json.loads(items)
    return ret_item["status"] == 200

def del_deck(username, token, deck_name):
    payload = {'username':username, 'token':token, 'deck_name':deck_name}
    items = requests.post(base_url + "del_deck", data = json.dumps(payloads))
    ret_item = json.loads(items)
    return ret_item["status"] == 200

def get_cards():
    items = requests.get(base_url + "get_cards")
    ret_item = items.json()
    return ret_item["data"]

################ Game Variables #########################
base_url = "https://mtg.jamesxu.ca/"
existingImages = glob.glob("Card Images/*")
card_database =get_cards()
for card in card_database:
    card_database[card] = Card(card,card_database)


current_screen = "Login Menu"
current_selection = "Nil"
typing = False
typing_reference = None
user_item = User()

cur_background = 0
bck_direction = 1

menu_specifications = {"Login Menu": {"Username":"Username", "Password":"Password"},
                       'Main Menu': {},
                       'Deck Building': {}
                       }

#Setting up pygame
original_screen = [800,600]
screen = pygame.display.set_mode(original_screen, pygame.RESIZABLE)


pygame.display.set_caption("HTN Program")
size_ratio = 1

original_images = {}
images_database = {}

path_way = os.path.dirname(os.path.realpath(__file__)) #Directory to the python file
for image in os.listdir(path_way+"/Images"): #Loading images
    save_path = "Images/" + image
    if image[-3:]=="jpg" or image[-3:]=="png":
        curImg = pygame.image.load(save_path)
        sizes = list(map(int,image[image.rfind("_")+1:image.rfind(".")].split("x")))
        original_images[image[:image.rfind("_")]] = [curImg, sizes[0], sizes[1]]


################ Connecting socket #########################
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = "localhost" 
port = 224
#server.connect((host_ip, port))
images_database = {}

def setup():
    global images_database
    for image in original_images:
        im = original_images[image][:]
        try:
            images_database[image] = pygame.transform.smoothscale(im[0], (int(size_ratio * im[1]), int(size_ratio * im[2])))
        except:
            images_database[image] = pygame.transform.scale(im[0], (int(size_ratio * im[1]), int(size_ratio * im[2])))
setup()
################ Game loop #########################
running = True
start = time.time()
first = True

while running:
    clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button==1: #They clicked with the left click
            clicked = True
        elif event.type == pygame.KEYDOWN and typing:
            if event.key == pygame.K_BACKSPACE:
                if len(typing_reference[current_selection]) >0:
                    typing_reference[current_selection] = typing_reference[current_selection][:-1]
                
            elif event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN: #Remove it
                typing = False
                typing_reference = None
                current_selection = "Nil"
                
            elif event.key < 256: #Add new char
                typing_reference[current_selection] += event.unicode
                
        elif event.type == pygame.VIDEORESIZE:
            print('resize')
            x,y = event.w,event.h
            requested_size = [x,y]
            ratio_wanted = original_screen[0]/original_screen[1]
            ratio_requested = requested_size[0]/requested_size[1]

            if ratio_requested > ratio_wanted + 0.01:
                requested_size[0] = int(requested_size[1]*ratio_wanted)
            elif ratio_requested < ratio_wanted - 0.01:
                requested_size[1] = int(requested_size[0]/ratio_wanted)

            size_ratio = requested_size[1]/original_screen[1]
            screen = pygame.display.set_mode(requested_size,pygame.RESIZABLE)

            #Resize images
            images_database = {}
            for image in original_images:
                im = original_images[image][:]
                try:
                    images_database[image] = pygame.transform.smoothscale(im[0], (int(size_ratio*im[1]), int(size_ratio*im[2])))
                except:
                    images_database[image] = pygame.transform.scale(im[0], (int(size_ratio*im[1]), int(size_ratio*im[2])))

    if clicked and typing: #Remove it
        typing = False
        typing_reference = None
        current_selection = "Nil"
    
    cur = time.time()
    mx,my = pygame.mouse.get_pos()

    sc_params = menu_specifications[current_screen]
    screen.fill((255,255,255))
    if current_screen == "Login Menu":
        cur_background += bck_direction
        if cur_background == 48 or cur_background == 0:
            bck_direction *= -1
            
        screen.blit(images_database["IntroGif%i"%(cur_background)],[int(e*size_ratio) for e in [0, 0]])
        for i in range(2):
            im_name, im_pos = ["Sign Up", "Sign In"][i], [[675,462],[675,537]][i]
            im_pos = [int(e*size_ratio) for e in im_pos]
            item = screen.blit(images_database[im_name], im_pos)
            if item.collidepoint(mx,my) and clicked: #They signed up or in!
                user_item.make_user(sc_params["Username"], sc_params["Password"], ["create_user", "sign_in"][i])

        #Username and password bars
        buttons = [transparent_rect(int(275*size_ratio), int(470*size_ratio), int(250*size_ratio), int(40*size_ratio), 120),
        transparent_rect(int(275*size_ratio), int(545*size_ratio), int(250*size_ratio), int(40*size_ratio), 120)]        

        for a in range(2):
            if buttons[a].collidepoint(mx,my) and clicked:
                current_selection = ["Username", "Password"][a]
                sc_params[current_selection] = ""
                typing = True
                typing_reference = sc_params
                
        
        largest_size1, x_taken1, y_taken, myfont1 = font_size("timesnewroman",sc_params["Username"],int(275*size_ratio),int(40*size_ratio),60)
        largest_size2, x_taken2, y_taken, myfont2 = font_size("timesnewroman",sc_params["Password"],int(275*size_ratio),int(40*size_ratio),60)

        mysize = largest_size1 < largest_size2 and largest_size1 or largest_size2
        myfont = pygame.font.SysFont("timesnewroman", mysize) #Make for both
        
        x_taken = pygame.font.Font.size(myfont,sc_params["Username"])[0]
        text_with_outline(sc_params["Username"] + (current_selection=="Username" and cur_background//8%2==0 and '|' or ""),myfont, (255,255,255), (0,0,0), int(400*size_ratio)-x_taken//2, int(472*size_ratio), 1, False)

        x_taken = pygame.font.Font.size(myfont,sc_params["Password"])[0]
        text_with_outline(sc_params["Password"] + (current_selection=="Password" and cur_background//8%2==0 and '|' or ""),myfont,(255,255,255), (0,0,0), int(400*size_ratio)-x_taken//2, int(547*size_ratio), 1, False)

        
    
    pygame.display.flip()
    time.sleep(0.04)
pygame.quit()
    





