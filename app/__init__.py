from flask import Flask
import os
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from authlib.integrations.flask_client import OAuth

application = app = Flask(__name__)
app.config.from_object(Config)

#csrf protection
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
csrf.init_app(app)

#url_for in javascript
from flask_jsglue import JSGlue
jsglue = JSGlue(app)

from sqlalchemy.ext.declarative import declarative_base
convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}
Base = declarative_base(convention)
#database
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True) #because sqlite can't alter without this

import boto3
s3_client = boto3.client("s3", region_name=str(app.config["S3_REGION"]), aws_access_key_id=str(app.config["S3_ACCESS_KEY"]), aws_secret_access_key=str(app.config["S3_SECRET_ACCESS_KEY"]))


#oauth stuff
"""CONF_URL = 'https://accounts.google.com/o/oauth2/auth'
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)"""
#lm = LoginManager(app)

from app import routes
#from app.CsrfDb import models
