[![Build Status](https://travis-ci.org/crichon/pyrss_backend.svg?branch=master)](https://travis-ci.org/crichon/pyrss_backend)

# pyrss_backend

An rss backend built with Flask and SqlAlchemy.

## Decription

Its goals is to provide a suitable json REST API in order to built an Rss reader upon it.

It exposes three objects types:
 - Feed: A feed object represent an Rss/ Atom feed sources.
 - Tags: Tags are used in order to filter Feed and Feed's items display.
 - Contents: The rss parsed items.

Routes:
 - /feed [CREATE, GET]
 - /feed/id [GET, PUT, DELETE]
 - /tag [CREATE, GET]
 - /tag/id [GET, PUT, DELETE]
 - /content [GET]
 - /content/id [GET]
 - /refresh [POST]

Feed and Tags exposes CRUD methods.
Contents can already be reads since they are created internally by the
feedparser update process (/refresh route).

## Launch

    pip -r requirements.txt
    gunicorn -w 4 launch:app

## Test

    pip -r requirements-dev.txt
    tox

## Roadmap

Create a web client using react and a ncurses one in python.

Todo:
 - Docker image
 - Streaming API in order to push live notification to clients on update
 - Search and filter API endpoint
 - Patch endpoint for updating content's star and read properties
 - Add authentification support
 - Extract and complete documentation

