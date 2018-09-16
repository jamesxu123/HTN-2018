import auth
import json
import re


class DeckHandler(auth.AuthObject):

    def retrieve_decks(self, username):
        if self.user_exists(username):
            cur = self.db.cursor()
            cur.execute("SELECT deck FROM users WHERE username = '%s';" % username)
            for row in cur.fetchall():
                deck = row[0]
                return deck
        return False

    def set_deck(self, username, new_deck_name, new_deck):
        if self.user_exists(username):
            cur = self.db.cursor()
            decks = self.retrieve_decks(username)
            if decks:
                decks = json.loads(decks)
            else:
                decks = {}
            if new_deck:
                decks[new_deck_name] = new_deck
            else:
                decks[new_deck_name] = []

            cur.execute("UPDATE users SET deck = %s WHERE username = '%s';" % (re.escape(json.dumps(new_deck)), username))

            self.db.commit()

            return True
        return False

    def del_deck(self, username, deck_name):
        cur = self.db.cursor()
        decks = self.retrieve_decks(username)

        decks = json.loads(decks)

        del decks[deck_name]

        cur.execute("UPDATE users SET deck = %s WHERE username = '%s';" % (re.escape(json.dumps(decks)), username))

        self.db.commit()

    def get_stats(self, username):
        cur = self.db.cursor()

        cur.execute("SELECT wins, losses FROM users WHERE username = '%s';" % username)

        for row in cur.fetchall():
            wins = row[0]
            losses = row[0]
            return {"wins": wins, "losses": losses}
        return False
