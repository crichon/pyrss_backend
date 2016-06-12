'''This module describe the models used by the API.

Provide the db object to interact with the database and
the models in use by the application.
'''

from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse

from .utils import get_feed_parser, get_tag_parser

db = SQLAlchemy()

feed_tag = db.Table('tags', db.metadata,
                 db.Column('left_id', db.Unicode, db.ForeignKey('feed.id')),
                 db.Column('right_id', db.Unicode, db.ForeignKey('tag.id'))
)

class Feed(db.Model):
    '''This class represent a feed sources.'''

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.Unicode, unique=True)
    name = db.Column(db.Unicode, unique=True)
    tags = db.relationship('Tag',
                            secondary=feed_tag,
                            cascade_backrefs=False,
                            backref=db.backref('feeds'))

    _parser = get_feed_parser()

    def __init__(self, source, name, tags, id=0):
        '''Feed constructor

        Args:
            source (str): the feed url
            name   (str): the feed name
            tags   (list): a list of string
        '''
        self.name = name
        self.source = source
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

        instance.update_tags(args['tags'])
        return instance

    def update_tags(self, tags):
        '''Merge existring tags with the given one'''

        old = set([tag.name for tag in self.tags])
        new = set(tags)

        to_delete = old - new
        for item in self.tags:
            if item.name in to_delete:
                self.tags.remove(item)

        for item in new - old: self.tags.append(create_or_get_tag(item))


class Content(db.Model):
    '''This class represent a feed's item.'''

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Unicode, unique=True)
    title = db.Column(db.Unicode)
    created_date = db.Column(db.DateTime, nullable=False)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'), nullable=False)
    feed = db.relationship('Feed',
                           backref=db.backref('contents', lazy='dynamic'))
    text = db.Column(db.UnicodeText)
    read = db.Column(db.Boolean)
    star = db.Column(db.Boolean)

    def __init__(self, content_id, url, title, created_date, text,
                 read=False, star=False, id=0):
        '''Content constructor.

        Args:
            content_id   (str): the rss feed's item
            url          (str): permalink
            title        (str): the item title
            # created_date (str): the item creation date
            text         (str): the item contents
            read         (bool): is the item marked as readed
            star         (bool): is the item marked as to_keep
            id           (int): Optional, content_id
        '''
        if self.__class__.query.get(id): self.id = id
        self.url = url
        self.title = title
        # self.created_date = created_date
        self.text = text
        self.read = read
        self.star = star
        self.feed = Feed.query.filter(Feed.name == feed).one()


class Tag(db.Model):
    '''This class represent a tag. Tag are associated with feeds.'''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)

    _parser = get_tag_parser()

    def __init__(self, name, id=0):
        '''Tag constructor.

        Args:
            name (str): the tag  name
            id   (int): Opitonal, the tag id
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

