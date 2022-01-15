import os
from dotenv import load_dotenv

# Absolute directory path
basedir = os.path.abspath(os.path.dirname(__file__))

# Looks for and loads .env file
# Can access env variables using os.environ.get(<VARNAME>)
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'th1515453cr3tk37'
    #generates a hidden field that includes a token that is used to protect the form against CSRF attacks
    
    #running from external database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    #running locally
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False #dont need a notification every time the database is changed
    #configure app.db database, store it in basedir.
    
    TEMPLATES_AUTO_RELOAD=True

    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY')
    S3_REGION = os.environ.get('S3_REGION')
    BUCKET_NAME = os.environ.get('BUCKET_NAME')
    BUCKET_NAME_RESUME = os.environ.get('BUCKET_NAME_RESUME')
    ACL = os.environ.get('ACL')
    UPLOAD_EXTENSIONS = os.environ.get('UPLOAD_EXTENSIONS')
    UPLOAD_EXTENSIONS_RESUME = os.environ.get('UPLOAD_EXTENSIONS_RESUME')