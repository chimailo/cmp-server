import random
from functools import wraps
from time import sleep

from flask import request, current_app
from api.errors import error_response
from api.models import User
from api.email import send_password_email


special_chars = ['~', '@', '#', '$', '%', '^', '&', '*', '/', '-', '+', ';', '?', '{', '}', '(', ')', '[', ']', '|', '_', '=']
numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return error_response(403, message='No authorization.')

        token = auth_header.split(" ")[1]
        payload = User.decode_auth_token(token)

        if not isinstance(payload, dict):
            return error_response(401, message=payload)

        user = User.find_by_id(payload.get('id'))

        if user is None:
            return error_response(401, message='Invalid token.')

        return func(user, *args, **kwargs)
    return wrapper


def generate_password(sentences):
    """Generate an alpha-numeric-char string from the given sentences 

    Args:
        sentences (list): An array of sentences

    Returns:
        string: A password string
    """
    chars = special_chars + numbers
    words = []
    count = 0

    for sentence in sentences:
        word = random.choice(sentence.split()).strip()
        words.append(word)
        count += len(word)

    chars = random.sample(special_chars + numbers, 5) if count >= 10 else \
        random.sample(special_chars + numbers, 10)
    sample = words + chars
    random.shuffle(sample)
    return ''.join(sample)


def generate_passwords(sentences, n):
    """Generate a list of passwords by calling generate_password() n times

    Args:
        sentences (list): An array of sentences
        n (list): Number of times to call generate_password()

    Returns:
        list: A list of password strings
    """
    return [generate_password(sentences) for i in range(n)]


def password_reminder(app, user):
    """Send the user an email periodically with a link to view their password 

    Args:
        user (User): The user object

    Returns:
        None
    """
    # run forever
    while True:
        # block for the interval
        sleep(user.password_reminder * 24 * 60 * 60)
        with app.app_context():
            # perform the task
            send_password_email(user, reset=True)
