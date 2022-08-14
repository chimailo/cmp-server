# Computing Masters Project - API

Welcome to Computing Masters Project.

## Project Setup

### Clone the repo to your local computer

```sh
git clone git@github.com:chimailo/cmp-server.git
```

### Change directory to where you downloaded the repo

```sh
cd cmp-server
```

### Install requirements

```sh
pip install -r requirements.txt
```

### Set environment variables

You will need to set up the following environment variables:

```sh
SECRET_KEY - A string of chars used to encode jwt
LOG_TO_STDOUT - Should logs be printed on the console?
MAIL_SERVER - A url to your (mailgun) email server.
DOMAIN_NAME - Your domain name.
WEB_CLIENT_BASE_URL - Url for the frontend client (https://computingmasters.netlify.app).
MAIL_SERVER_API_KEY - API key for the (mailgun) email server.
DATABASE_URL - A url string representing a path to the database.
```

### Seed the questions table

```sh
flask seed questions-table
```

### Start the server

```sh
flask run
```

## Using the API's

Once the server is running, you can start making requests. [View the api documentation](https://code.visualstudio.com/) (https://documenter.getpostman.com/view/6054133/VUjSG49H).