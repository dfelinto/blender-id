from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Create app
app = Flask(__name__)
import config
app.config.from_object(config.Development)

# Create database connection object
db = SQLAlchemy(app)

from application import model
from application import controller
