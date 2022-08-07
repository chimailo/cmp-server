import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace(
    #     'postgres://', 'postgresql://') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY='an-extremely-long-key'
    POSTS_PER_PAGE=20
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    # token
    TOKEN_EXPIRATION_DAYS = 3
    TOKEN_EXPIRATION_SECONDS = 0
