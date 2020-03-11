from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import psycopg2
from sqlalchemy import create_engine
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from datetime import datetime
from hashlib import md5

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' 


app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'

#app.config.from_object(Config)
#db = SQLAlchemy(app)
#migrate = Migrate(app, db)
#from app import routes, models

#Switch EVB to "dev" when working local and 'prod' when deployed to heroku
ENV = 'prod'

if ENV == 'work_dev':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:gelaw01@localhost/flask_test'
    engine = create_engine('postgresql://postgres:gelaw01@localhost/flask_test')
elif ENV == 'home_dev':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_user:123abc@localhost/flask_test'
    engine = create_engine('postgresql://flask_user:123abc@localhost/flask_test')
else: 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://bxtcmazytjltgd:7cca2b76b2925e4d872ff735e597a0b726a86a71f17b2941e1819df40edb0c20@ec2-184-72-235-159.compute-1.amazonaws.com:5432/d1a21ond0jpa2g'
    engine = create_engine('postgres://bxtcmazytjltgd:7cca2b76b2925e4d872ff735e597a0b726a86a71f17b2941e1819df40edb0c20@ec2-184-72-235-159.compute-1.amazonaws.com:5432/d1a21ond0jpa2g')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#run python
#   from app import db
#   db.create_all() ##this makes tables

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('all_users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('all_users.id'))
)

class Userdreams(db.Model):
    __tablename__= 'userdreams'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True)
    user_dream = db.Column(db.String(100))

    def __init__(self, user_name, user_dream):
        self.user_name = user_name
        self.user_dream = user_dream

class User(UserMixin, db.Model):
    __tablename__= 'all_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    observation = db.relationship('Observation', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Observation.query.join(
            followers, (followers.c.followed_id == Observation.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Observation.timestamp.desc())

class Observation(db.Model):
    __tablename__= 'observation'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('all_users.id'))
    #narrative_like = db.relationship('narratives_likes', backref='narratives', lazy='dynamic')
    #narrative_like = db.relationship('Narrative', secondary='narrative_likes', backref='User', lazy='dynamic')

    def __init__(self, body, timestamp, user_id):
        self.body = body
        self.timestamp = timestamp
        self.user_id = user_id

def followed_posts(self):
    followed = Observation.query.join(
        followers, (followers.c.followed_id == Observation.user_id)).filter(
            followers.c.follower_id == self.id)
    own = Observation.query.filter_by(user_id=self.id)
    return followed.union(own).order_by(Observation.timestamp.desc())

#db.Table('narrative_likes',
#    db.Column('user_id', db.Integer, db.ForeignKey('all_users.id')),
#    db.Column('narrative_id', db.Integer, db.ForeignKey('narratives.id')))

#class NarrativeLikes(db.Model):
#    __tablename__= 'narratives_likes'
#    id = db.Column(db.Integer, primary_key=True)
#    user_id = db.Column(db.Integer, db.ForeignKey('all_users.id'))
#    narrative_id = db.Column(db.Integer, db.ForeignKey('narratives.id'))

#    def __init__(self, user_id, narrative_id):
#        self.user_id = user_id
#        self.narrative_id = narrative_id

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

from app import routes
