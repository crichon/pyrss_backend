# coding: utf-8

import os
from unittest.mock import patch

import pytest
from flask import json

import pyRss

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
        'source': 'shaarli.terminus.crichon.eu?do=rss',
        'tags': ['leisure']
    },
    'content': {
        'url': 'feed/1',
        'title': 'mytitle',
        'text': 'a wonderful article',
        'read': True,
        'star': False
    }
}

@pytest.fixture(scope='module')
def app(request):
    '''Return a ready to use application test client'''

    def teardown():
        os.remove(TESTING_DB.replace('sqlite:///', ''))

    request.addfinalizer(teardown)

    pyRss.app.config['SQLALCHEMY_DATABASE_URI'] = TESTING_DB
    with pyRss.app.app_context():
        pyRss.db.init_app(pyRss.app)
        pyRss.init_db()
        pyRss.register_api(pyRss.app)
        return pyRss.app.test_client()


@pytest.fixture(params=['tag', 'feed'])
def endpoint(request):
    return request.param, data[request.param]

def test_api(app, endpoint):
    endpoint, playload = endpoint

    # test empty
    assert to_dict(app.get('/' + endpoint).data) == []

    # test post
    response = app.post(
        '/' + endpoint, data=json.dumps(playload), headers=HEADERS
    )
    playload['id'] = 1
    assert to_dict(response.data) == playload

    # test get/id
    assert to_dict(app.get('/' + endpoint + '/1').data) == playload

    # test put
    if endpoint == 'feed': playload['tags'] = ['leisure_']
    playload['name'] += '_'
    response = app.put(
        '/' + endpoint + '/1', data=json.dumps(playload), headers=HEADERS
    )
    assert to_dict(response.data) == playload

    # test get/
    assert len(to_dict(app.get('/' + endpoint).data)) == 1

    # test errors
    assert app.get('/' + endpoint + '/5').status_code == 404
    assert app.post('/' + endpoint, data=json.dumps({}), headers=HEADERS)\
           .status_code == 400
    assert app.put('/' + endpoint + '/1', data=json.dumps({}),
                   headers=HEADERS).status_code == 400
    assert app.put('/' + endpoint + '/5', data=json.dumps({}),
                   headers=HEADERS).status_code == 404
    assert app.delete('/' + endpoint + '/5').status_code == 404

    # test delete
    assert to_dict(app.delete('/' + endpoint + '/1').data) == playload

