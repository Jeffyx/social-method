from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import psycopg2

app = Flask(__name__, static_url_path='/static')
#app.config.from_object(Config)
#db = SQLAlchemy(app)
#migrate = Migrate(app, db)
#from app import routes, models

#Switch EVB to "dev" when working local and 'prod' when deployed to heroku
ENV = 'PROD'

if ENV == 'dev':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_user:123abc@localhost/flask_test'
else: 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://bxtcmazytjltgd:7cca2b76b2925e4d872ff735e597a0b726a86a71f17b2941e1819df40edb0c20@ec2-184-72-235-159.compute-1.amazonaws.com:5432/d1a21ond0jpa2g'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Userdreams(db.Model):
    __tablename__= 'userdreams'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True)
    user_dream = db.Column(db.String(100))

    def __init__(self, user_name, user_dream):
        self.user_name = user_name
        self.user_dream = user_dream

from app import routes
