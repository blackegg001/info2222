ALTER TABLE User
ADD COLUMN salt VARCHAR(32);

UPDATE User SET salt = '1c412654190c0e18a0cfca3b7d7a106e' WHERE username = 'blackegg';


CREATE TABLE Friends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_username1 VARCHAR(255) NOT NULL,
    user_username2 VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_username1) REFERENCES Users(username),
    FOREIGN KEY (user_username2) REFERENCES Users(username),
    UNIQUE(user_username1, user_username2)
);
DELETE FROM Friends WHERE user_username1 = 'subject1' AND user_username2 = 'blackegg';


CREATE TABLE Friendrequest (
    sender VARCHAR(255) NOT NULL,
    receiver VARCHAR(255) NOT NULL,

    FOREIGN KEY (sender) REFERENCES Users(username),
    FOREIGN KEY (receiver) REFERENCES Users(username),
    UNIQUE(sender, receiver)
);




ALTER TABLE Friendrequest DROP PRIMARY KEY;
ALTER TABLE Friendrequest DROP COLUMN id;
ALTER TABLE Friendrequest ADD PRIMARY KEY (sender, receiver);


ALTER TABLE Friendrequest
ADD COLUMN status TEXT NOT NULL DEFAULT 'pending';


CREATE TABLE Chatrecords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chatroom_id INT NOT NULL,
    sender VARCHAR(255) NOT NULL,
    receiver VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender) REFERENCES Users(username),
    FOREIGN KEY (receiver) REFERENCES Users(username)
);

CREATE TABLE Chatroom (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    creator VARCHAR(255) NOT NULL,
    participant VARCHAR(255) NOT NULL,
);
INSERT INTO chatroom (id, creator, participant)
VALUES (1, 'blackegg', 'jarvis');

INSERT INTO chatroom (id, creator, participant)
VALUES (2, 'blackegg', 'subject1');

DELETE FROM chatroom
WHERE creator = 'blackegg' AND participant = 'subject1';


ALTER TABLE Chatroom DROP COLUMN created_at;
ALTER TABLE Chatroom DROP COLUMN name;

INSERT INTO user (username, password) VALUES
('jarvis', '123456');

INSERT INTO Friends (user_username1, user_username2) VALUES
('blackegg', 'jarvis');

alter table user
add column onlinestatus boolean default false;

alter table user
add column role text default "none";

alter table user
add column last_chatroom_id default false;


ALTER TABLE user
RENAME TO Userinfo;

CREATE TABLE UserArticles (
    article_id INT AUTO_INCREMENT PRIMARY KEY,
    userName  VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    commentName  VARCHAR(255) NOT NULL,
    comment TEXT NOT NULL,
);

CREATE TABLE IF NOT EXISTS Comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    commentName TEXT NOT NULL,
    comment TEXT NOT NULL,
    FOREIGN KEY (article_id) REFERENCES UserArticles (article_id)
);



