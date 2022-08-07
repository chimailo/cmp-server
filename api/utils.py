import random
from functools import wraps
from datetime import datetime

from flask import request
from api.errors import error_response
from api.models import User


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

    for sentence in sentences:
        words.append(random.choice(sentence.split()).strip())

    chars = random.sample(special_chars + numbers, 12)
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
