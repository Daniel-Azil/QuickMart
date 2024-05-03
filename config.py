"""
    A separate file that config flask to use the system environment set by
    load_dotenv from the .env file in the current dir.
"""

from os import getenv
from dotenv import load_dotenv
from flask import Flask


app = Flask(__name__)


load_dotenv()
"""
    load_dotenv function automatically loads .env file
    and store the .env variables into the operating system environment.
"""


# we now load the environment variable on the .env file straight from the os and no the .env
# file os which the load_dotenv has made it an actual environment variable.
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".jpeg"]
app.config["UPLOAD_PATH"] = "static/images"
