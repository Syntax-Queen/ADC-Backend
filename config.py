import os
from dotenv import load_dotenv
 
load_dotenv() #load .env variables

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + 'ADC.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False