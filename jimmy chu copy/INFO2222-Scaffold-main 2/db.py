'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *
import sqlite3
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
i = 1
j = 1
def clear():
    with Session(engine) as session:
        session.query(UserArticles).delete()
        session.commit()
# inserts a user to the database
def insert_user(username: str, password: str, salt, role):
    with Session(engine) as session:
        user = User(username=username, password=password, salt=salt, role=role)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username):
    with Session(engine) as session:
        print(f"Debug: Querying for user with username - {username}")
        user = session.query(User).filter_by(username=username).first()
        print(f"Debug: Retrieved user with query - {user}")
        return user
    
def get_role(username):
    with Session(engine) as session:
        info = session.query(User).filter_by(username=username).first()
        return info.role

#get friendrequest
def get_friendlist(username):
    with Session(engine) as session:
        bruh = session.query(Friend).filter(Friend.user_username1 == username).all()
        friend_usernames = [friend.user_username2 for friend in bruh]

        users = session.query(User).filter(User.username.in_(friend_usernames)).all()
        userlist = []

        # Debug print information for each user
        #print("Friend List Information:")
        #for user in users:
            # Assuming User is a mapped class with known attributes
            #print(f"User: {user.username}")
            # Print out all column information using vars or other attributes directly
            #user_info = vars(user)
            #print(f"User Info: {user_info}")

        for u in users:
            if u.onlinestatus == False:
                status = "offline"
            elif u.onlinestatus == True:
                status = "online"
            else:
                status = "unknown"

            userlist.append(f"{u.username}, role:{u.role}, status: {status}")
            print(f"Debug: {u.username}, role:{u.role} status: {status}")

        return userlist

#save friend
def save_friend(username1, username2):
    with Session(engine) as session:
        friend1 = Friend(user_username1=username1, user_username2=username2)
        friend2 = Friend(user_username2=username1, user_username1=username2)
        session.add(friend1)
        session.add(friend2)
        session.commit()

#get friendrequest
def get_friendrequest(sender, receiver):
    with Session(engine) as session:
        if sender and receiver:
            print(f"Debug: Querying for friend request with sender - {sender} and receiver - {receiver}")
            return session.query(Friendrequest).filter_by(sender=sender, receiver=receiver).first()
        return None

    '''
    with Session(engine) as session:
        friend1 = session.query(Friend).filter(Friend.user_username1 == username1, Friend.user_username2 == username2).first()
        friend2 = session.query(Friend).filter(Friend.user_username1 == username2, Friend.user_username2 == username1).first()
        if friend1 and friend2:
            return True
        return False
    '''

#save friendrequest
def save_friendrequest(sender, receiver):
    with Session(engine) as session:
        if sender and receiver:
            friend_request = Friendrequest(sender=sender, receiver=receiver)
            session.add(friend_request)
            session.commit()
            return True
        return False

        '''
        friendrequest = Friendrequest(sender_username=sender, receiver_username=receiver)
        session.add(friendrequest)
        session.commit()'''

#get friendrequestlist for display
def get_friendrequestlist(user):
    '''
    with Session(engine) as session:
        if user: 
            requests = session.query(Friendrequest).filter_by(receiver=user).all()
            request_details = [request.sender+", status:"+ request.status for request in requests]
            return request_details
        return []
    '''
    
    with Session(engine) as session:
        if user:
            # Query to get all friend requests 
            requests = session.query(Friendrequest).filter(
                (Friendrequest.sender == user) | (Friendrequest.receiver == user)
            ).all()

            # Generate details for each request
            request_details = []
            for request in requests:
                if request.sender == user:
                    detail = f"You sent a request to {request.receiver}, status: {request.status}"
                else:
                    detail = f"{request.sender} sent you a request, status: {request.status}"
                request_details.append(detail)

            return request_details
        return []
    
def delete_friendrequest(sender, receiver):
    with Session(engine) as session:
        if sender and receiver:
            friend_request = session.query(Friendrequest).filter_by(sender=sender, receiver=receiver).first()
            session.delete(friend_request)
            session.commit()
            print(f"Debug: Deleted friend req")
            return True
        return False
    
def get_friends(username1, username2):
    with Session(engine) as session:
        friend1 = session.query(Friend).filter(Friend.user_username1 == username1, Friend.user_username2 == username2).first()
        friend2 = session.query(Friend).filter(Friend.user_username1 == username2, Friend.user_username2 == username1).first()
        if friend1 and friend2:
            return True
        return False
    

# save a room to the database
def save_room(creator: str, participant: str):
    with Session(engine) as session:
        if creator and participant:
            room = Chatroom(creator=creator, participant=participant)
            session.add(room)
            session.commit()
            print(f"Debug: Saved room")
            return True
        return False
    
# get a room from the database
def get_room(creator_name: str, recver_name: str):
    with Session(engine) as session:
        room1 = session.query(Chatroom).filter_by(creator=creator_name, participant=recver_name).first()
        print(f"Debug: room1 - {room1}")
        room2 = session.query(Chatroom).filter_by(creator=recver_name, participant=creator_name).first()
        print(f"Debug: room2 - {room2}")
        if room1 is not None:
            return room1.id
        elif room2 is not None:
            return room2.id
        else:
            return None


# save chat message to the database
def save_message(roomid: int, sender: User, receiver: User, message:str):
    with Session(engine) as session:
        if sender and receiver:
            
            print(f"Debug: Saving message")
            chat_message = Chatrecord(chatroom_id=roomid, sender=sender, receiver=receiver, message=message)
            session.add(chat_message)
            session.commit()
            print(f"Debug: Saved message")
            return True
        return False

# get chat message from the database
def get_messagelist(sender: str, receiver: str):
    with Session(engine) as session:
        if sender and receiver:
            # get room id
            #room_id = get_room(sender, receiver)
               
            chat_records = session.query(Chatrecord).filter_by(receiver=sender, sender=receiver).all()
    
            messages_content = [{"sender": msg.sender, "content": msg.message} for msg in chat_records]
            #print(f"Debug: Retrieved messages{messages_content}")
            return messages_content
        return []


def change_status(username, status):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.onlinestatus = status
        session.commit()

def deletefriend(username1, username2):
    with Session(engine) as session:
        friend1 = session.query(Friend).filter(Friend.user_username1 == username1, Friend.user_username2 == username2).first()
        friend2 = session.query(Friend).filter(Friend.user_username1 == username2, Friend.user_username2 == username1).first()
        session.delete(friend1)
        session.delete(friend2)
        session.commit()

#Used to remove user with specific username        
def delete_user(username: str):
    with Session(engine) as session:
        user_to_delete = session.query(User).filter_by(username=username).first()
        if user_to_delete is not None:
            session.delete(user_to_delete)
            session.commit()
            print(f"User '{username}' has been successfully deleted.")
        else:
            print(f"Error: User '{username}' is not in the database.")

def store_article(userName, title, content):
    global i
    with Session(engine) as session:
        try:
            article = UserArticles(userName=userName, title=title, content=content, article_id = i)
            i += 1
            session.add(article)
            session.commit()
            return True  # Success
        except Exception as e:
            session.rollback()
            print(f"Error storing article: {e}")
            return False  # Failed

def modify_article(article_id, content):
    with Session(engine) as session:
        try:
            article_to_modify = session.query(UserArticles).filter_by(article_id = article_id).first()
            article_to_modify.content = content
            session.commit()
            return True  # Success
        except Exception as e:
            session.rollback()
            print(f"Error storing article: {e}")
            return False  # Failed

def modify_title(article_id, content):
    with Session(engine) as session:
        try:
            title_to_modify = session.query(UserArticles).filter_by(article_id = article_id).first()
            title_to_modify.title = content
            session.commit()
            return True  # Success
        except Exception as e:
            session.rollback()
            print(f"Error storing article: {e}")
            return False  # Failed


def store_comment(article_id, commentName, comment):
    global j
    with Session(engine) as session:
        try:
            # Query the UserArticles table to find the article with the given article_id
            article = session.query(UserArticles).filter_by(article_id=article_id).first()
            if article:
                # Create a new comment
                new_comment = Comments(comment_id = j, article_id=article_id, commentName=commentName, comment=comment)
                j += 1
                session.add(new_comment)
                session.commit()
                return True  # Success
            else:
                print(f"Article with article_id {article_id} not found.")
                return False
        except Exception as e:
            session.rollback()
            print(f"Error storing comment: {e}")
            return False  # Failed

def get_articles_by_username(username):
    with Session(engine) as session:
        try:
            user = session.query(UserArticles).filter_by(userName=username).first()
            if user:
                all = session.query(UserArticles).filter_by(userName=username).all()
                article_ids = [a.article_id for a in all]
                articles = [a.content for a in all]
                titles = [a.title for a in all]
                comments = [a.comment for a in all]
                commentNames = [a.commentName for a in all]
                return [article_ids, articles, titles, comments, commentNames]
            else:
                print("no")
                return []  # User not found
        except Exception as e:
            print(f"Error retrieving articles: {e}")
            return None  # Failed
        
def get_all_articles():
    with Session(engine) as session:
        try:
            all_articles = session.query(UserArticles).all()
            if all_articles:
                userNames = [a.userName for a in all_articles]
                article_ids = [a.article_id for a in all_articles]
                articles = [a.content for a in all_articles]
                titles = [a.title for a in all_articles]

                # Retrieve comments for each article
                comments = []
                commentNames = []
                comment_ids = []
                for article in all_articles:
                    article_comments = session.query(Comments).filter_by(article_id=article.article_id).all()
                    commentNames.append([c.commentName for c in article_comments])
                    comments.append([c.comment for c in article_comments])
                    comment_ids.append([c.comment_id for c in article_comments])
                return [userNames, article_ids, articles, titles, comments, commentNames, comment_ids]
            else:
                print("No articles found.")
                return []  # No articles found
        except Exception as e:
            print(f"Error retrieving articles: {e}")
            return None  # Failed to retrieve articles

def delete_article(deleteChoice):
    try:
        with sqlite3.connect('database/main.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM UserArticles WHERE article_id = ?", (deleteChoice,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def delete_comment(deleteChoice):
    try:
        with sqlite3.connect('database/main.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Comments WHERE comment_id = ?", (deleteChoice,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def mute(username):
    with Session(engine) as session:
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                user.muteStatus = True
                session.commit()
            else:
                return []  # User not found
        except Exception as e:
            print(f"Error retrieving articles: {e}")
            return None  # Failed
        
def unmute(username):
    with Session(engine) as session:
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                user.muteStatus = False
                session.commit()
            else:
                return []  # User not found
        except Exception as e:
            print(f"Error retrieving articles: {e}")
            return None  # Failed


def get_mute(username):
    with Session(engine) as session:
        info = session.query(User).filter_by(username=username).first()
        return info.muteStatus
    
# Example usage:
# articles = get_articles_by_username(session, username="blackegg")
# for article in articles:
#     print(f"Title: {article.title}, Content: {article.content}")

def drop_table(table_name):
    try:
        # Connect to your database
        connection = sqlite3.connect('database/main.db')
        cursor = connection.cursor()

        # Execute the DROP TABLE statement
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        # Commit the changes
        connection.commit()
        print(f"Table '{table_name}' dropped successfully!")

    except sqlite3.Error as e:
        print(f"Error dropping table: {e}")

    finally:
        # Close the connection
        connection.close()

def create_tables():
    try:
        with sqlite3.connect('database/main.db') as conn:
            cursor = conn.cursor()
            # Execute the CREATE TABLE statements
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS UserArticles (
                    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    userName VARCHAR(255) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    commentName TEXT ,
                    comment TEXT 
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Comments (
                    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    commentName TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    FOREIGN KEY (article_id) REFERENCES UserArticles (article_id)
                );
            """)
            # Commit the changes
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")