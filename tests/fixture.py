'''Shared data and fixture used by the tests'''
import json
import os
import time
from datetime import datetime
from unittest.mock import patch

import pytest

import pyrss_backend
from  pyrss_backend.models import Content, Feed


TESTING_DB = 'sqlite:////tmp/testing.db'
HEADERS = {'Content-type': 'application/json'}

def to_dict(py_object):
    '''Convert bytes response data to dict'''
    if isinstance(py_object, bytes):
        return json.loads(py_object.decode('UTF-8'))
    return py_object

data = {
    'tag': {'name': 'leisure'},
    'feed': {
        'name': 'crichon_shaarli',
        'source': 'http://shaarli.terminus.crichon.eu?do=rss',
        'tags': ['leisure']
    },
    'content': {
        'object_id': 'test',
        'feed': 1,
        'link': 'feed/1',
        'title': 'mytitle',
        'text': 'a wonderful article',
        'created_date': datetime(*time.localtime()[:6]),
        'read': True,
        'star': False
    }
}

# @pytest.fixture(scope='module')
@pytest.fixture()
def app(request):
    '''Return a ready to use application test client'''

    def teardown():
        os.remove(TESTING_DB.replace('sqlite:///', ''))

    request.addfinalizer(teardown)

    test_app = pyrss_backend.init_app()
    test_app.config['SQLALCHEMY_DATABASE_URI'] = TESTING_DB
    with test_app.app_context():
        pyrss_backend.db.init_app(test_app)
        pyrss_backend.init_db()
        pyrss_backend.register_api(test_app)
        test_app.register_blueprint(
            pyrss_backend.routes.refresh_blueprint
        )
        return test_app.test_client()

@pytest.fixture()
def app_with_content(request):
    '''Return a ready to use application test client'''

    def teardown():
        os.remove(TESTING_DB.replace('sqlite:///', ''))

    request.addfinalizer(teardown)

    test_app = pyrss_backend.init_app()
    test_app.config['SQLALCHEMY_DATABASE_URI'] = TESTING_DB
    with test_app.app_context():
        pyrss_backend.db.init_app(test_app)
        pyrss_backend.init_db()

        pyrss_backend.db.session.add(Feed(**data['feed']))
        pyrss_backend.db.session.commit()
        content = Content(**data['content'])
        pyrss_backend.db.session.add(content)
        pyrss_backend.db.session.commit()

        pyrss_backend.register_api(test_app)
        test_app.register_blueprint(
            pyrss_backend.routes.refresh_blueprint
        )
        return test_app.test_client()

