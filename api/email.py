from urllib.parse import urlencode
import requests
from flask import current_app


def send_password_email(user, reset=False, password=None):
    token = user.encode_auth_token(password=password, reset_password=reset)
    route = '/reset-password' if reset else '/password'
    url = current_app.config['WEB_CLIENT_BASE_URL'] + \
        f'/#/{route}' + urlencode({'qs': token})
    html = get_password_reset_html(url, user.username) if reset \
        else get_new_user_html(url, user.username)
    response = requests.post(
        current_app.config['MAIL_SERVER'],
        auth=("api", f"{current_app.config['MAIL_SERVER_API_KEY']}"),
        data={"from": f"Computing Masters Project <mailgun@{current_app.config['DOMAIN_NAME']}.com>",
              "to": ["collins.chima.ilo@gmail.com", user.email],
              "subject": "Password",
              "html": html})

    if not response.ok:
        raise requests.RequestException('An error has occurred')
    return response


def get_new_user_html(url, username):
    return f'<p>Dear {username},</p> \
    <p>Let me welcome you to Computing Masters Project, I hope you have a swell time here.</p> \
    <p>When you signed up to use our service you selected a password, to view it click the button below</p><br /> \
    <a href="{url}" style="margin-top: 32px; margin-bottom: 32px; padding: 13px 28px; background-color: #990f3d; color: #fff; border-radius: 4px; text-decoration: none;"> \
        View your Password \
    </a> \
    <br /> \
    <p>Alternatively, you can paste the following link in your browser address bar:</p> \
    <p>{url}</p> \
    <p>If you have not requested a password reset simply ignore this message.</p> \
    <p>Sincerely,</p> \
    <p>Computing Masters Project</p>'


def get_password_reset_html(url, username):
    return f'<p>Dear {username },</p> \
    <p>A new password has been generated for you. Click the button below to view it.</p> <br /> \
    <a href="{url}" style="margin-top: 32px; margin-bottom: 32px; padding: 13px 28px; background-color: #990f3d; color: #fff; border-radius: 4px; text-decoration: none;"> \
        View your Password \
    </a> \
    <br /> \
    <p>Alternatively, you can paste the following link in your browser address bar:</p> \
    <p>{url}</p> \
    <p>If you have not requested a password reset simply ignore this message.</p> \
    <p>Sincerely,</p> \
    <p>Computing Masters Project</p>'
