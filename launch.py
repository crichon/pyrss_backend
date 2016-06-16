#!/usr/bin/env python

from gevent.wsgi import WSGIServer

from pyrss_backend import (
    init_app, db, init_db, register_api, refresh_blueprint
)

app = init_app()
TESTING_DB = 'sqlite:////tmp/testing.db'
app.config['SQLALCHEMY_DATABASE_URI'] = TESTING_DB

db.init_app(app) # flask_sqlalchemy initialisation

with app.app_context():
    db.create_all()

register_api(app)
app.register_blueprint(refresh_blueprint)

if __name__ == '__main__':
    app.run(debug=True)

