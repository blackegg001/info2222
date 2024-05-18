'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, jsonify
from flask_socketio import SocketIO
import db
import secrets
import os
import hashlib
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)
username = ""
last_user = ""
showItems = False
user_inputs = {}
# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)
db.drop_table("UserArticles")
db.drop_table("Comments")
db.create_tables()
# don't remove this!!
import socket_routes
class MyForm(FlaskForm):
    user_input = StringField('Write something:', validators=[DataRequired()])
    submit = SubmitField('Submit')

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
    global last_user
    last_user = ""
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

'''
@app.route('/formm', methods=['GET', 'POST'])
def formm():
    print("a")
    form = MyForm()
    if form.validate_on_submit():
        user_text = form.user_input.data
        return render_template('repository.jinja', user_text=user_text)
    print("a")
    return render_template('repository.jinja', form=form)
'''


# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

@app.route("/repository",  methods=['GET', 'POST'])
def repository():
    global user_inputs,showItems
    form = MyForm()
    if form.validate_on_submit():
        showItems = True
        user_text = form.user_input.data
        if user_inputs.get(username) != None:
            user_inputs[username].append(user_text)
        else:
            user_inputs[username] = [user_text]
        print(user_inputs.get(username) != None)
        print(user_inputs)
        return render_template('repository.jinja', showItems = showItems, username = username, user_text=user_text, form=form, user_inputs=user_inputs[username])
    
    return render_template('repository.jinja', showItems = showItems, username = username, form=form, user_inputs = [])

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
        global last_user
        last_user = ""
        if not request.is_json:
            abort(404)
        username = request.json.get("username")
        if username == "":
            return "Error: Username cannot be empty" 
        password = request.json.get("password")
        if password == "":
            return "Error: Username cannot be empty"
        salt = generate_salt()
        if db.get_user(username) is None:
            db.insert_user(username, password, salt)
            return url_for('home', username=username)
        return "Error: User already exists!"

@app.route("/repository/user", methods=["POST"])
def repository_user():
    return url_for('repository', username = username)

@app.route("/msg/user", methods=["POST"])
def msg_user():
    return url_for('home', username = username)

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    global username,friendlist,friendreqlist,last_user
    if username != "" and last_user == username:
        return render_template("home.jinja", username=username, friend_list=friendlist, friend_req_list=friendreqlist)
    if request.args.get("username") is None:
        abort(404)
    username = request.args.get("username") 
    last_user = username
    friendlist = db.get_friendlist(request.args.get("username"))
    friendreqlist = db.get_friendrequestlist(request.args.get("username"))
    return render_template("home.jinja", username=username, friend_list=friendlist, friend_req_list=friendreqlist)
    
@app.route('/submit_article', methods=['POST'])
def submit_article():
    data = request.get_json()
    user_title = data.get('userTitle')
    article_content = data.get('articleContent')
    db.store_article(username,user_title,article_content)

    return 'Article submitted successfully!'

@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    data = request.get_json()
    article_id = data.get('commentChoice')
    comment = data.get('commentContent')
    db.store_comment(article_id,username,comment)
    return 'Comment submitted successfully!'

@app.route('/delete_article', methods=['POST'])
def delete_article():
    data = request.get_json()
    delete_id = data.get('deleteChoice')
    db.delete_article(delete_id)
    return 'Comment submitted successfully!'

@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    data = request.get_json()
    delete_id = data.get('deleteChoice')
    db.delete_comment(delete_id)
    return 'Comment submitted successfully!'

@app.route('/get_article', methods=['GET'])
def get_article():
    article_id, content, title, comment, commentName= db.get_articles_by_username(username)
    data = {"content": content, "title": title, "article_id": article_id, "commentName": commentName, "comment": comment}
    return jsonify(data)

@app.route('/get_articles', methods=['GET'])
def get_articles():
    userName, article_id, content, title, comment, commentName, comment_id= db.get_all_articles()
    data = {"content": content, "title": title, "article_id": article_id, "commentName": commentName, "comment": comment, "userName": userName, "commentId": comment_id}
    return jsonify(data)


if __name__ == '__main__':
    socketio.run(app)
