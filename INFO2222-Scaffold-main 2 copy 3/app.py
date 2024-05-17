'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for
from flask_socketio import SocketIO
import db
import secrets
import os
import hashlib

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# Function to generate a salt
def generate_salt(length=16):
    return os.urandom(length)

# Function to hash a password with a salt
def hash_password(password, salt):
    if isinstance(salt, str):
        salt_bytes = bytes.fromhex(salt)  
    else:
        salt_bytes = salt
    return hashlib.sha256(password.encode('utf-8') + salt_bytes).hexdigest()

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password") # this is the password that the user entered
    print(f"user-{username}, password-{password}")
    

    user =  db.get_user(username)
    print(user.password)# this is the password that is stored in the database
    hashed_password_database = hash_password(user.password, user.salt)
    hashed_password_input = hash_password(password, user.salt)
    if user is None:
        return "Error: Username or Password does not exist!"

    if hashed_password_database != hashed_password_input:
        return "Error: Username or Password does not match!"
    
    db.change_status(username, True)
    print(f"{username} is now online!!!")

    return url_for('home', username=request.json.get("username"))

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
        if not request.is_json:
            abort(404)
        username = request.json.get("username")
        password = request.json.get("password")
        role = request.json.get("role")
        print(f"user-{username}, password-{password}, role-{role}")

        salt = generate_salt()

        if db.get_user(username) is None:
            db.insert_user(username, password, salt, role)
            return url_for('home', username=username)
        return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)
    friendlist = db.get_friendlist(request.args.get("username"))
    friendreqlist = db.get_friendrequestlist(request.args.get("username"))
    return render_template("home.jinja", username=request.args.get("username"), friend_list=friendlist, friend_req_list=friendreqlist)



if __name__ == '__main__':
    socketio.run(app)
