'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    print(f"Debug: {username} has connected to room {room_id}")
    db.change_status(username, True)
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    print(f"Debug: {username} has disconnected from room {room_id}")
    db.change_status(username, False)
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))

# send message event handler
@socketio.on("send")
def send(username, message, room_id):

    emit("incoming", (f"{username}: {message}"), to=room_id)

    receiver = room.get_room_receiver(int(room_id), username)
    print(f"Debug: {username} has sent a {message} to {receiver} in room {room_id}")

     # Check if a room exists in the database for the two users; if not, create it
     # Attempt to retrieve an existing room
    db_room_id = db.get_room(username, receiver)
    print(f"Debug: db_room_id: {db_room_id}")
    # Check if the room was found
    if db_room_id is None:
        # If no room exists, create a new one
        db_room_id = db.save_room(username, receiver)

    print(f"creating room with {username}-username and {receiver}-receiver with id {db_room_id}")
    # Store the message in the database
    db.save_message(db_room_id, username, receiver, message)
    print(f"Debug: saved: {username} sent a {message} to {receiver}")
'''

'''
    
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)

    # if the user is already inside of a room 
    if room_id is not None:
        
        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        # emit only to the sender
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        
        msglist = db.get_messagelist(sender_name, receiver_name)
        print(f"Debug: {msglist}")
        if len(msglist) > 0:
            for i in msglist:
                sender = i['sender']
                content = i['content']
                #print(f"Debug: sender type - {type(sender)}, content type - {type(content)}")  # Check data types
                print(f"Debug: {sender} sent {content}")
                emit("incoming", (f"{sender}: {content}.", "green"))
        return room_id

    # if the user isn't inside of any room, 
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)

    
    msglist = db.get_messagelist(sender_name, receiver_name)
    print(f"Debug: {msglist}")
    if len(msglist) > 0:
        for i in msglist:
            sender = i['sender']
            content = i['content']
            #print(f"Debug: sender type - {type(sender)}, content type - {type(content)}")  # Check data types
            print(f"Debug: {sender} sent {content}")
            emit("incoming", (f"{sender}: {content}.", "green"))
            #emit("incoming", {"type": "status", "data": {"message": f"yoyo", "color": "green"}}, room=room_id)
    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)


@socketio.on("requestfriend")
def handle_friendrequest(username, requsername):
    
    print(f"Debug: {username} has sent a friend request to {requsername}")
    #check if they are already friends
    if db.get_friends(username, requsername):
        return "You are already friends!"
    #check if user exists
    if db.get_user(requsername) is None:
        return "User does not exist!"
    #check if request already exists
    if db.get_friendrequest(username, requsername):
        return "Friend request already exists!"
    #save friend request
    db.save_friendrequest(username, requsername)
    return "Friend request sent!"
    '''
    emit("incoming", (f"{sender} has sent a friend request to {receiver}"), to=room.get_room_id(receiver))
    emit("incoming", (f"{sender} has sent a friend request to {receiver}"), to=room.get_room_id(sender))
    '''

@socketio.on("acceptfriend")
def handle_acceptfriend(sender, receiver):

    print(f"Debug: sender-{sender}, receiver-{receiver}")
    
    #check if they are already friends
    if db.get_friends(sender, receiver):
        return "You are already friends!"
    #check if user exists
    if not db.get_user(receiver):
        return "User does not exist!"
    #check if request exists
    if not db.get_friendrequest(sender, receiver):
        return "Friend request does not exist!"
    #save friend
    db.save_friend(sender, receiver)
    #delete friend request
    db.delete_friendrequest(sender, receiver)
    return "Friend request accepted!"
    
@socketio.on("rejectfriend")    
def handle_declinefriend(sender, receiver):
    #check if they are already friends
    if db.get_friends(sender, receiver):
        return "You are already friends!"
    #check if user exists
    if not db.get_user(receiver):
        return "User does not exist!"
    #check if request exists
    if not db.get_friendrequest(sender, receiver):
        return "Friend request does not exist!"
    #delete friend request
    db.delete_friendrequest(sender, receiver)
    return "Friend request declined!"

@socketio.on("unfriend")
def handle_unfriend(sender, receiver):
    print(f"Debug: sender-{sender} trying to delete receiver-{receiver}")
    #check if they are already friends
    if not db.get_friends(sender, receiver):
        return "You are not friends!"
    #check if user exists
    if not db.get_user(receiver):
        return "User does not exist!"
    #delete friend
    db.deletefriend(sender, receiver)
    print(f"Debug: {sender} has deleted {receiver}")
    return "Friend removed!"