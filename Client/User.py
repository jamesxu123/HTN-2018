# User class for keeping track of profile things
import requests
from Deck import *
from GlobalVar import *
import json


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
            self.token = ret_item["token"]
            self.name = username
            self.get_data()
            global current_screen
            current_screen = "Main Menu"
            print("Account success")
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
