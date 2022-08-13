import re
from marshmallow import Schema, fields, validate, ValidationError, validates, post_load
from api.models import Answer, Question, Sentence, User

class UserSchema(Schema):
    id = fields.Str(dump_only=True, validate=validate.Length(max=32))
    username = fields.Str(
        validate=validate.Length(min=3, max=32),
        required=True,
        error_messages={"required": "Username is required."}
    )
    email = fields.Email(
        required=True, error_messages={"required": "Email is required."})
    password = fields.Str(load_only=True)
    age = fields.Int(validate=validate.Range(min=18))
    password_reminder = fields.Int(required=True, validate=validate.Range(min=1))
    country = fields.Str(validate=validate.Length(min=3, max=255))
    sex = fields.Str(validate=validate.OneOf(['male', 'female', 'rather not say']))
    created_on = fields.DateTime(dump_only=True)
    sentences = fields.List(fields.Nested('SentenceSchema', required=True))
    answers = fields.List(fields.Nested('AnswerSchema', required=True))

    @validates('username')
    def validate_username(self, username):
        if re.match('^[a-zA-Z0-9_]+$', username) is None:
            raise ValidationError(
                'Username can only contain a-z, A-Z, 0-9, -, _ characters.'
            )
        if User.find_by_username(username):
            raise ValidationError('A user with that username already exists')

    @validates('email')
    def validate_email(self, email):
        if User.find_by_email(email):
            raise ValidationError('A user with that email already exists')


class SentenceSchema(Schema):
    id = fields.Str(dump_only=True, validate=validate.Length(max=32))
    text = fields.Str(required=True)
    userId = fields.Str(dump_only=True)

    @post_load
    def make_sentence(self, data, **kwargs):
        return Sentence(**data)


class AnswerSchema(Schema):
    id = fields.Str(dump_only=True, validate=validate.Length(max=32))
    text = fields.Str(required=True)
    questionId = fields.Str(required=True)
    userId = fields.Str(dump_only=True)

    @post_load
    def make_answer(self, data, **kwargs):
        return Answer(**data)


class QuestionSchema(Schema):
    id = fields.Str(dump_only=True, validate=validate.Length(max=32))
    text = fields.Str(required=True)

    @post_load
    def make_question(self, data, **kwargs):
        return Question(**data)