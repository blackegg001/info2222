'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password: str):
    with Session(engine) as session:
        user = User(username=username, password=password)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username):
    with Session(engine) as session:
        return session.get(User, username)

def get_friendlist(username):
    with Session(engine) as session:
        bruh = session.query(Friend).filter(Friend.user_username1 == username).all()
        friend_usernames = [friend.user_username2 for friend in bruh]

        return friend_usernames

def save_friend(username1, username2):
    with Session(engine) as session:
        friend1 = Friend(user_username1=username1, user_username2=username2)
        friend2 = Friend(user_username2=username1, user_username1=username2)
        session.add(friend1)
        session.add(friend2)
        session.commit()