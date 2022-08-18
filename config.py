import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'an-extremely-long-key'
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # token
    TOKEN_EXPIRATION_DAYS = 3
    TOKEN_EXPIRATION_SECONDS = 0
    PASSWORD_TOKEN_EXPIRATION_HRS = 60 * 60
    # mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
    WEB_CLIENT_BASE_URL = os.environ.get('WEB_CLIENT_BASE_URL')
    MAIL_SERVER_API_KEY = os.environ.get('MAIL_SERVER_API_KEY')
