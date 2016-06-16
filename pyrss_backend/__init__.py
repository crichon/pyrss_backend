'''pyrss_backend

A simple rss backend using flask and sqlalchemy.
'''
import json

from flask import Flask

# expose initialisation functions
from .models import db, init_db
from .views import register_api
from .routes import refresh_blueprint

def init_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # set default refresh interval to 10 min
    app.config.setdefault('UPDATE_PERIOD', 600)
    return app

