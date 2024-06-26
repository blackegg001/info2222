'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Dict
from sqlalchemy import Column, Integer, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import ForeignKey

# data models
class Base(DeclarativeBase):
    pass

# model to store user information
from sqlalchemy import Boolean  # Import the Boolean class from sqlalchemy

class User(Base):
    __tablename__ = "Userinfo"
    
    # looks complicated but basically means
    # I want a username column of type string,
    # and I want this column to be my primary key
    # then accessing john.username -> will give me some data of type string
    # in other words we've mapped the username Python object property to an SQL column of type String 
    username: Mapped[str] = mapped_column(String, primary_key=True)
    password: Mapped[str] = mapped_column(String)
    salt: Mapped[int] = mapped_column(Integer)
    onlinestatus = Column(Boolean, nullable=False, default=False)
    role = Column(String, nullable=False, default="None")
    
class Friend(Base):
    __tablename__ = "Friends"
    
    # id = Column(Integer, primary_key=True, autoincrement=True)
    #user_username1 = Column(String(255), ForeignKey('user.username'), nullable=False)
    #user_username2 = Column(String(255), ForeignKey('user.username'), nullable=False)

    user_username1 = Column(String(255), primary_key=True, nullable=False)
    user_username2 = Column(String(255), primary_key=True, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_username1', 'user_username2', name='unique_user1_user2'),
    )
    
class Friendrequest(Base):
    __tablename__ = "Friendrequest"
    
    #id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(String(255), ForeignKey('user.username'), nullable=False)
    receiver = Column(String(255), ForeignKey('user.username'), nullable=False)
    receiver: Mapped[str] = mapped_column(String, primary_key=True)
    status = Column(String, default="pending")

    __table_args__ = (
        UniqueConstraint('sender', 'receiver', name='unique_sender_receiver'),
    )

class Chatrecord(Base):
    __tablename__ = "Chatrecord"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chatroom_id = Column(Integer, nullable=False)

    sender = Column(String(255), ForeignKey('user.username'), nullable=False)
    receiver = Column(String(255), ForeignKey('user.username'), nullable=False)
    message = Column(String, nullable=False)


class Chatroom(Base):
    __tablename__ = "Chatroom"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    #name = Column(String(255), nullable=False)
    creator = Column(String(255), ForeignKey('user.username'), nullable=False)
    participant = Column(String(255), ForeignKey('user.username'), nullable=False)




# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter

# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of 
        # the room where John is in
        self.dict: Dict[str, int] = {}
    
    def get_room_receiver(self, room_id: int, exclusion: str):
        print(self.dict)
        for key, value in self.dict.items():
            if value == room_id and key != exclusion:
                return key
        return None

    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        return room_id
    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.dict[sender] = room_id

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]

    # gets the room id from a user
    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]
    
class UserArticles(Base):
    __tablename__ = "UserArticles"

    userName: Mapped[str] = mapped_column(String(255), nullable=False)
    article_id = Column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

