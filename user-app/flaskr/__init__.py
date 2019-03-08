from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskr.config import Config
import boto3

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
s3 = boto3.client('s3')

from flaskr import home
from flaskr import login
from flaskr import upload
from flaskr import error