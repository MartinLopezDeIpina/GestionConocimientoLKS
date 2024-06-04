import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clavesecreta'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://postgres:123@localhost/tasks'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
