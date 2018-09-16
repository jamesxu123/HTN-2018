import MySQLdb as sql
from argon2 import PasswordHasher
import uuid


class AuthObject:
    def __init__(self, hostaddr, username, password, dbname):
        self.db = sql.connect(host=hostaddr,
                              user=username,
                              password=password,
                              db=dbname)
        self.logged_in = {}

    def user_exists(self, username):
        cur = self.db.cursor()
        print("SELECT * FROM users WHERE username = '%s';" % (username))
        cur.execute("SELECT * FROM users WHERE username='%s';" % (username))

        if cur.rowcount < 1:
            return False
        else:
            return True

    def create_user(self, username, password):
        if not self.user_exists(username):
            ph = PasswordHasher()
            hashed = ph.hash(password)
            cur = self.db.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES ('%s','%s');"  # Execute insertion query
                        % (username, hashed))

            self.db.commit()  # Commit changes
            return True
        else:
            return False

    def sign_in(self, username, password):
        ph = PasswordHasher()
        cur = self.db.cursor()
        if self.user_exists(username):
            cur.execute("SELECT password FROM users WHERE username = '%s';" % username)
            for row in cur.fetchall():
                if ph.verify(row[0], password):
                    token = uuid.uuid4()
                    self.logged_in[username] = str(token)
                    return str(token)
                else:
                    return False
        else:
            return False

    def sign_out(self, username):
        if username in self.logged_in:
            self.logged_in.remove(username)
