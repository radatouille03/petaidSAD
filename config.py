import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkeyforpetaidassignment3'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///petaid.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
