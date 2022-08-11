import random
import re
from sqlalchemy import exc
from marshmallow import ValidationError, Schema, fields
from flask import request, url_for, Blueprint, jsonify

from api import db
from api.schema import QuestionSchema, UserSchema
from api.models import Question, User
from api.errors import error_response, bad_request, server_error
from api.utils import generate_passwords, authenticate
from api.email import send_reset_password_email

users = Blueprint('users', __name__, url_prefix='/api/users')
sentences = Blueprint('sentences', __name__, url_prefix='/api/sentences')


@sentences.route('/ping')
def ping():
    return {"message": "Sentences Route!"}


@sentences.route('/validate', methods=['POST'])
def validate_sentence():
    post_data = request.get_json()

    if not post_data:
        return bad_request("No input data provided")

    if len(post_data) != 3:
        return bad_request('You must enter 3 sentences')

    try:
        sentences = []
        for sentence in post_data:
            count = len(re.findall(r'\w+', sentence))
            if count > 10 or count < 5:
                raise ValidationError(
                    'All the sentences must be between 5 and 10 words')
            sentences.append(sentence)
    except ValidationError as err:
        return error_response(422, err.messages[0])

    try:
        questions = Question.query.all()

        passwords = generate_passwords(sentences, 3)
        return {
            'passwords': passwords,
            'questions': QuestionSchema().dump(questions, many=True)
        }
    except exc.SQLAlchemyError as err:
        print(err)
        return server_error('Something went wrong, please try again.')


@users.route('/ping')
def ping():
    return {"message": "Users Route!"}


@users.route('/validate', methods=['POST'])
def validate_user():
    post_data = request.get_json()

    if not post_data:
        return bad_request("No input data provided")

    try:
        data = UserSchema().load(post_data, partial=('answers', 'sentences',))
    except ValidationError as err:
        return error_response(422, err.messages)
    return {}


@users.route('', methods=['POST'])
def create_user():
    post_data = request.get_json()

    if not post_data:
        return bad_request("No input data provided")

    try:
        data = UserSchema().load(post_data)
    except ValidationError as err:
        return error_response(422, err.messages)

    email = data.get('email')
    username = data.get('username')
    answers = data.get('answers')
    sentences = data.get('sentences')

    if User.find_by_username(username):
        return bad_request(
            {'username': ['A user with that username already exists']}
        )

    if User.find_by_email(email):
        return bad_request(
            {'email': ['A user with that email already exists']}
        )

    user = User()
    user.email = email
    user.username = username
    user.location = data.get('location')
    user.age = data.get('age')
    user.sex = data.get('sex')
    user.password = User.hash_password(data.get('password'))
    user.password_reminder = data.get('password_reminder')
    user.answers = answers
    user.sentences = sentences

    try:
        user.save()
    except:
        db.session.rollback()
        return server_error('Something went wrong, please try again.')
    # try:
    send_reset_password_email(user)
    # except Exception:
    #     return server_error('An error occurred while trying to send \
    #         you a reset link. Please try again.')

    response = jsonify({'token': user.encode_auth_token()})
    response.status_code = 201
    response.headers['Location'] = url_for('users.get_user', id=user.id)
    return response


@users.route('/validate-login', methods=['POST'])
def validate_login():
    post_data = request.get_json()

    RequestSchema = Schema.from_dict({
        "identity": fields.Str(required=True),
        "password": fields.Str(required=True),
    })

    try:
        data = RequestSchema().load(post_data)
    except ValidationError as error:
        return bad_request(error.messages)

    if data is None:
        return bad_request("No input data provided")

    try:
        # check for existing user
        user = User.find_by_identity(data['identity'])

        if user and user.check_password(data['password']):
            questions = Question.query.all()
            question = random.choice(questions)

            return {
                'userId': user.id,
                'question': QuestionSchema().dump(question)
            }
        else:
            return error_response(401, 'Invalid credentials.')
    except Exception:
        return server_error('Something went wrong, please try again.')


@users.route('/login', methods=['POST'])
def login():
    post_data = request.get_json()

    RequestSchema = Schema.from_dict({
        "userId": fields.Str(required=True),
        "questionId": fields.Str(required=True),
        "answer": fields.Str(required=True)
    })

    try:
        data = RequestSchema().load(post_data)
    except ValidationError as error:
        return error_response(422, error.messages)

    if data is None:
        return bad_request("No input data provided")

    try:
        user = User.find_by_id(data['userId'])

        if user is None:
            return error_response(401, 'User does not exist.')
    except Exception:
        return server_error('Something went wrong, please try again.')

    try:
        question = Question.find_by_id(data['questionId'])

        if question is None:
            return error_response(401, 'That question does not exist.')
    except Exception:
        return server_error('Something went wrong, please try again.')

    try:
        answer_text = question.get_user_answer(user)

        if answer_text != data['answer']:
            return error_response(401, 'Invalid credentials')
        return {'token': user.encode_auth_token()}
    except Exception:
        return server_error('Something went wrong, please try again.')


@users.route('/validate-user', methods=['POST'])
def validate_user_email():
    post_data = request.get_json()

    RequestSchema = Schema.from_dict({"email": fields.Email(required=True)})

    try:
        data = RequestSchema().load(post_data)
    except ValidationError as error:
        return bad_request(error.messages[0])

    if data is None:
        return bad_request("No input data provided")

    if not User.find_by_email(data['email']):
        return bad_request('User does not exist.')

    try:
        questions = Question.query.all()
        return QuestionSchema().dump(random.choice(questions))
    except exc.SQLAlchemyError as err:
        print(err)
        return server_error('Something went wrong, please try again.')


@users.route('/forgot-password', methods=['POST'])
def forgot_password():
    post_data = request.get_json()

    RequestSchema = Schema.from_dict({
        "email": fields.Email(required=True),
        "questionId": fields.Str(required=True),
        "answer": fields.Str(required=True)
    })

    try:
        data = RequestSchema().load(post_data)
    except ValidationError as error:
        return bad_request(error.messages)

    if data is None:
        return bad_request("No input data provided")

    try:
        user = User.find_by_email(data['email'])

        if user is None:
            return error_response(401, 'User does not exist.')
    except Exception:
        return server_error('Something went wrong, please try again.')

    try:
        question = Question.find_by_id(data['questionId'])

        if question is None:
            return error_response(401, 'That question does not exist.')
    except Exception:
        return server_error('Something went wrong, please try again.')

    try:
        answer_text = question.get_user_answer(user)

        if answer_text != data['answer']:
            return error_response(401, 'Incorrect answer')
    except Exception:
        return server_error('Something went wrong, please try again.')

    # try:
    send_reset_password_email(user, reset=True)
    return {'message': 'A message has been sent to your email'}
    # except Exception:
    #     return server_error('An error occurred while trying to send you a reset link. Please try again.')


@users.route('/question', methods=['GET'])
def get_question():
    try:
        question = random.choice(Question.query.all())
    except Exception:
        return server_error('Something went wrong, please try again.')
    return {'question': QuestionSchema().dump(question)}
    

@users.route('/password', methods=['POST'])
def reset_password():
    post_data = request.get_json()

    RequestSchema = Schema.from_dict({
        "token": fields.Str(required=True),
        "questionId": fields.Str(required=True),
        "answer": fields.Str(required=True)
    })

    try:
        data = RequestSchema().load(post_data)
    except ValidationError as error:
        return bad_request(error.messages)

    if data is None:
        return bad_request("No input data provided")

    payload = User.decode_auth_token(data['token'])

    if not isinstance(payload, dict):
        return error_response(401, message=payload)

    user = User.find_by_id(payload.get('id'))

    if user is None:
        return error_response(401, message='Invalid token.')

    try:
        question = Question.find_by_id(data['questionId'])

        if question is None:
            return error_response(401, 'That question does not exist.')
    except Exception:
        return server_error('Something went wrong, please try again.')

    try:
        answer_text = question.get_user_answer(user)

        if answer_text != data['answer']:
            return error_response(401, 'Incorrect answer')
    except Exception:
        return server_error('Something went wrong, please try again.')

    sentences = [sentence.text for sentence in user.sentences]
    password = generate_passwords(sentences, 1)[0]
    user.password = User.hash_password(password)

    try:
        user.save()
        return {'password': password}
    except:
        db.session.rollback()
        return server_error('Something went wrong, please try again.')


@users.route('/validate-email', methods=['POST'])
@authenticate
def validate_email(user):
    post_data = request.get_json()

    RequestSchema = Schema.from_dict({"email": fields.Email(required=True)})

    try:
        data = RequestSchema().load(post_data)
    except ValidationError as error:
        return bad_request(error.messages[0])

    if data is None:
        return bad_request("No input data provided")

    if User.find_by_email(data['email']):
        return bad_request("A user with that email already exists")

    try:
        questions = Question.query.all()
        return QuestionSchema().dump(random.choice(questions))
    except exc.SQLAlchemyError as err:
        print(err)
        return server_error('Something went wrong, please try again.')


@users.route('', methods=['PUT'])
@authenticate
def change_email(user):
    post_data = request.get_json()

    RequestSchema = Schema.from_dict({
        "email": fields.Email(required=True),
        "questionId": fields.Str(required=True),
        "answer": fields.Str(required=True)
    })

    try:
        data = RequestSchema().load(post_data)
    except ValidationError as error:
        return bad_request(error.messages)

    if data is None:
        return bad_request("No input data provided")

    if User.find_by_email(data['email']):
        return bad_request("A user with that email already exists")

    try:
        question = Question.find_by_id(data['questionId'])

        if question is None:
            return error_response(401, 'That question does not exist.')
    except Exception:
        return server_error('Something went wrong, please try again.')

    try:
        answer_text = question.get_user_answer(user)

        if answer_text != data.get('answer'):
            return error_response(401, 'Invalid credentials')

        user.email = data.get('email')
        user.save()
        return UserSchema(exclude=['answers', 'sentences']).dump(user)
    except Exception:
        return server_error('Something went wrong, please try again.')


@users.route('/logout', methods=['GET'])
@authenticate
def logout_user(user):
    return {'message': 'Successfully logged out.'}


@users.route('', methods=['GET'])
@authenticate
def get_user(user):
    return UserSchema(exclude=['answers', 'sentences']).dump(user)
