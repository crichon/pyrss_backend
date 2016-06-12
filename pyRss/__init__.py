from flask import Flask

from .models import init_db, db
from .views import register_api

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

