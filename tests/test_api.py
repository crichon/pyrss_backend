'''Test models and view by simulating call to the backend'''
from copy import deepcopy

import pytest
from flask import json

from fixture import app, app_with_content, to_dict, data, HEADERS


@pytest.fixture(params=['tag', 'feed'])
def endpoint(request):
    return request.param, deepcopy(data[request.param])

def test_api(app, endpoint):
    endpoint, playload = endpoint

    # test empty
    assert to_dict(app.get('/' + endpoint).data) == []

    # test post
    response = app.post(
        '/' + endpoint, data=json.dumps(playload), headers=HEADERS
    )
    playload['object_id'] = 1
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


def test_content_api(app_with_content):

    expected = deepcopy(data['content'])

    expected['created_date'] = expected['created_date'].strftime('%Y-%m-%dT%H:%M:%S')
    expected['feed'] = data['feed']['name']
    expected['feed_id'] = 1

    print(app_with_content.get('/content').data)
    assert to_dict(app_with_content.get('/content').data) == [expected]

