'''Routes.py

This module decribe routes binded to action, not resources.
'''
import os
import logging

from flask import Blueprint, jsonify

from .updater import update

refresh_blueprint = Blueprint('/refresh', __name__)

LOG = logging.getLogger(__name__)


@refresh_blueprint.route('/refresh', methods=['POST'])
def refresh_feeds():
    '''Ask for an update'''
    try:
        os.mkfifo('/tmp/pyrss_update_lock')
        update_info = update()
        response = jsonify(update_info)
        response.status_code = 200
        os.remove('/tmp/pyrss_update_lock')
        return response
    except FileExistsError:
        response = jsonify('update is currently in progress, please wait.')
        response.status_code = 200
        return response
    except Exception as e:
        msg = 'Exception occured while updating feed\'s items'
        os.remove('/tmp/pyrss_update_lock')
        LOG.error(msg)
        LOG.error(e, exc_info=True)
        response = jsonify(msg)
        response.status_code = 500
        return response

