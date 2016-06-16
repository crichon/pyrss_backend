'''Test routes, refresh and refresh_state'''
from unittest.mock import patch

import os
import pytest

from fixture import app, to_dict

@pytest.fixture(params=[True, False])
def switch(request):
    return request.param

def test_refresh_ok(app):
    with patch('pyrss_backend.routes.update') as update:
        response = {'feeds_updated': 0, 'new_items': 0}
        update.return_value = response
        assert to_dict(app.post('/refresh').data) == response

def test_refresh_concurent(app):
    os.mkfifo('/tmp/pyrss_update_lock')
    with patch('pyrss_backend.routes.update') as update:
        assert app.post('/refresh').status_code == 200
        assert not update.called
    os.remove('/tmp/pyrss_update_lock')

def test_refresh_error(app):
    with patch('pyrss_backend.routes.update') as update:
        update.side_effect = RuntimeError('error on feed update')
        assert app.post('/refresh').status_code == 500

