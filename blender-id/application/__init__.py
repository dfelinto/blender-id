from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

# Create app
app = Flask(__name__)
import config
app.config.from_object(config.Development)

# Create database connection object
db = SQLAlchemy(app)

mail = Mail(app)

from application import model
from application import controller
