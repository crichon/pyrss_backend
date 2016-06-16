'''Updater.py

This modules handle feed's parsing and contents updating.

TODO:
 - needs a bit of refacotring in order to ease tests.
 - handle feed_item update
'''
import logging
import time
from datetime import datetime
from pprint import pformat

import feedparser

from .models import db, Content, Feed

LOG = logging.getLogger(__name__)


def update():
    '''Parse feed items and add them to the db.'''
    start_time = time.time()
    update_info = {'feeds_updated': 0, 'new_items': 0}
    feed_item = {}

    feeds = Feed.query.all()

    for feed in feeds:
        parser = feedparser.parse(feed.source,
                                  etag=feed._etag,
                                  modified=feed._modified)

        if parser.status in [301, 302]:
            LOG.info('Feed %s is redirected.', feed.name)
        elif parser.status == '410':
            LOG.warning('Feed %s is gone.', feed.name)
            continue
        elif parser.status != 200:
            LOG.error('%s return %d', feed.name, parser.status)
            continue

        feed.etag = parser.get('etag')
        feed.modified = parser.get('modified')
        db.session.merge(feed)

        for item in parser.entries:
            try:
                feed_item['object_id'] = item['id']
            except KeyError:
                LOG.warning('Error parsing feed %s. No id', feed.name)
                LOG.warning(pformat(item))
                continue

            if Content.query.get(feed_item['object_id']):
                continue # skip the iteration if the item already exist

            for key in ['title', 'link']:
                feed_item[key] = getattr(item, key, None)

            if 'created_parsed' in item:
                created_date = item['created_parsed']
            elif 'updated_parsed' in item:
                created_date = item['updated_parsed']
            else:
                created_date = time.localtime() # default to parse date
            feed_item['created_date'] = datetime(*created_date[:6])

            feed_item['text'] = item.get('contents')
            if feed_item['text']:
                feed_item['text'] = '\n'.join(feed_item['text'])
            else:
                feed_item['text'] = item.get('summary')

            feed_item['feed'] = feed.object_id

            content = Content(**feed_item)
            db.session.add(content)

            feed_item.clear()
            update_info['new_items'] += 1
        update_info['feeds_updated'] += 1
        db.session.commit() # commit by parsed feed

    update_info['time_spent'] = time.time() - start_time
    return update_info

