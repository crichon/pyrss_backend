'''This module describe the models used by the API.

Provide the db object to interact with the database and
the models in use by the application.
'''
from flask_sqlalchemy import SQLAlchemy

from .utils import get_feed_parser, get_tag_parser

db = SQLAlchemy()

FEED_TAG = db.Table(
    'tags', db.metadata,
    db.Column('left_id', db.Unicode, db.ForeignKey('feed.object_id')),
    db.Column('right_id', db.Unicode, db.ForeignKey('tag.object_id')))

class Feed(db.Model):
    '''This class represent a feed sources.'''

    object_id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.Unicode, unique=True)
    name = db.Column(db.Unicode, unique=True)
    tags = db.relationship('Tag',
                           secondary=FEED_TAG,
                           backref=db.backref('feeds'))
    _etag = db.Column(db.Unicode)
    _modified = db.Column(db.Unicode)

    _parser = get_feed_parser()

    def __init__(self, source, name, tags):
        '''Feed constructor

        Args:
            source (str): the feed url
            name   (str): the feed name
            tags   (list): a list of string
        '''
        self.name = name
        self.source = source
        self._etag = None
        self._modified = None
        if not tags is None:
            for item in tags: self.tags.append(create_or_get_tag(item))

    def dump(self):
        '''Return a dict representation of the object'''
        data = {k: v for k, v in vars(self).items() if not k.startswith('_')}
        data['tags'] = [tag.name for tag in self.tags]
        return data

    @classmethod
    def create(cls):
        '''Parse request inputs and create a feed instance'''
        args = cls._parser.parse_args()
        return cls(**args)

    @classmethod
    def update(cls, feed_id):
        '''Fetch a feed from the database and update its field'''
        instance = cls.query.get(feed_id)
        if not instance:
            raise LookupError('Feed with id %s not found.' % feed_id)
        args = cls._parser.parse_args()

        for key, value in args.items():
            if not key == 'tags':
                setattr(instance, key, value)

        instance.update_tags(args.get('tags'))
        return instance

    def update_tags(self, tags):
        '''Merge existring tags with the given one'''

        if tags is None: # skip if no tags are supplied
            return

        old = set([tag.name for tag in self.tags])
        new = set(tags)

        to_delete = old - new
        for item in self.tags:
            if item.name in to_delete:
                self.tags.remove(item)

        for item in new - old: self.tags.append(create_or_get_tag(item))


class Content(db.Model):
    '''This class represent a feed's item.'''

    object_id = db.Column(db.Unicode, primary_key=True)
    link = db.Column(db.Unicode)
    title = db.Column(db.Unicode)
    created_date = db.Column(db.DateTime, nullable=False)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.object_id'), nullable=False)
    feed = db.relationship('Feed',
                           backref=db.backref('contents', lazy='dynamic'))
    text = db.Column(db.UnicodeText)
    read = db.Column(db.Boolean)
    star = db.Column(db.Boolean)

    def __init__(self, object_id, link, title, text, feed, created_date,
                 read=False, star=False):
        '''Content constructor.

        Args:
            object_id   (str): the rss feed's item id
            url          (str): permalink
            title        (str): the item title
            # created_date (str): the item creation date
            text         (str): the item contents
            read         (bool): is the item marked as readed
            star         (bool): is the item marked as to_keep
        '''
        self.object_id = object_id
        self.link = link
        self.title = title
        self.created_date = created_date
        self.text = text
        self.read = read
        self.star = star
        self.feed = Feed.query.get(feed)

    def dump(self):
        '''Return a dict representation of the object'''
        data = {k: v for k, v in vars(self).items() if not k.startswith('_')}
        data['created_date'] = self.created_date.strftime('%Y-%m-%dT%H:%M:%S')
        data['feed'] = self.feed.name
        return data


class Tag(db.Model):
    '''This class represent a tag. Tag are associated with feeds.'''

    object_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)

    _parser = get_tag_parser()

    def __init__(self, name):
        '''Tag constructor.

        Args:
            name (str): the tag  name
        '''
        self.name = name

    def dump(self):
        '''Return a dict representation of the object.'''
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    @classmethod
    def create(cls):
        '''Create a new instance using flask-restfull request parser'''
        args = cls._parser.parse_args()
        return cls(**args)

    @classmethod
    def update(cls, tag_id):
        '''Update an existing tag'''
        instance = cls.query.get(tag_id)
        if not instance:
            raise LookupError('Tag with id %s not found' % tag_id)
        args = cls._parser.parse_args()
        instance.name = args['name']
        return instance


def init_db():
    '''Create the database and its tables.'''
    db.create_all()

def create_or_get_tag(item):
    '''Fetch a tag from the database or create it'''
    tag = Tag.query.filter(Tag.name == item).first()
    if not tag:
        tag = Tag(item)
    return tag

