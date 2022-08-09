import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace(
        'postgres://', 'postgresql://') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'an-extremely-long-key'
    POSTS_PER_PAGE=20
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    # token
    TOKEN_EXPIRATION_DAYS = 3
    TOKEN_EXPIRATION_SECONDS = 0
    PASSWORD_TOKEN_EXPIRATION_HRS = 1
    # mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['kollign@yahoo.com']
