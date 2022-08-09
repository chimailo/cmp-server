from base64 import b64encode
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from sqlalchemy import or_
from flask import current_app
from api import db


class Sentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdOn = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f'<Sentence {self.text}>'


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    answers = db.relationship('Answer', backref='answer')

    def __repr__(self):
        return f'<Question {self.text}>'

    @classmethod
    def find_by_id(cls, id):
        """
        Get a class instance given its id

        :param id: ID
        :type id: int
        :return: Class instance
        """
        return cls.query.get(int(id))

    def get_user_answer(self, user):
        return Answer.query.with_parent(self).filter(
            Answer.userId == user.id).first().text


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'))

    def __repr__(self):
        return f'<Answer {self.text}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), index=True, unique=True, nullable=False)
    email = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255))
    sex = db.Column(db.String(8))
    age = db.Column(db.Integer)
    password_reminder = db.Column(db.Integer)
    location = db.Column(db.String(255))
    created_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    sentences = db.relationship('Sentence', backref='user')
    answers = db.relationship('Answer', backref='user')

    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return f'<User {self.username}>'
    
    @classmethod
    def find_by_id(cls, id):
        """
        Get a class instance given its id

        :param id: ID
        :type id: int
        :return: Class instance
        """
        return cls.query.get(int(id))

    @classmethod
    def find_by_email(cls, email):
        user = cls.query.filter(cls.email == email).first()
        return user

    @classmethod
    def find_by_username(cls, username):
        user = cls.query.filter(cls.username == username).first()
        return user
    
    @classmethod
    def find_by_identity(cls, identity):
        user = cls.query.filter(
            or_(cls.email == identity, cls.username == identity)).first()
        return user

    @classmethod
    def hash_password(cls, password):
        if password:
            return generate_password_hash(password)

        return None

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def encode_auth_token(self, reset_password=False):
        """Generates the auth token"""
        expiration = None
        
        if reset_password:
            expiration = timedelta(seconds=current_app.config.get('PASSWORD_TOKEN_EXPIRATION_HRS'))
        else:
            expiration = timedelta(days=current_app.config.get('TOKEN_EXPIRATION_DAYS'), seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
                )
        try:
            payload = {
                'exp': datetime.utcnow() + expiration,
                'iat': datetime.utcnow(),
                'sub': {
                    'id': self.id,
                }
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(token):
        """
        Decodes the auth token

        :param string: token
        :return dict: The user's identity
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config.get('SECRET_KEY'),
                algorithms='HS256'
            )
            return payload.get('sub')
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def save(self):
        """
        Save a model instance.

        :return: Model instance
        """
        db.session.add(self)
        db.session.commit()

        return self
    