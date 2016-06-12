'''This modules provide the basic CRUD API on resources.

It implement a class factory using type and generic
CRUD method.
Aguments validation and relations handling are delegated to
the models.

Finnaly it provide an helper function to register the
API with the flask application.
'''

from flask_restful import reqparse, Api, Resource

from . import app
from .models import db, Tag, Feed, Content

from pprint import pprint

def _get(self, object_id):
    '''Return an object based on its id.'''
    instance = self.Model.query.get(object_id)
    if instance: return instance.dump(), 200
    return '', 404

def _delete(self, object_id):
    '''Delete an object based on its id.'''
    instance = self.Model.query.get(object_id)
    if instance:
        dump = instance.dump()
        db.session.delete(instance)
        return dump , 200
    return '', 404

def _put(self, object_id):
    '''Overwrite an object given its id.'''
    try:
        instance = self.Model.update(object_id)
        db.session.merge(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance.dump(), 200
    except LookupError as error:
        return error.args[0], 404

def _post(self):
    '''Add a new object.'''
    instance = self.Model.create()
    db.session.add(instance)
    db.session.commit()
    db.session.refresh(instance)
    return instance.dump(), 200

def _get_all(self):
    '''Return all objects contained in a collection.'''
    return [item.dump() for item in self.Model.query.all()], 200


def factory(name, model, mapping):
    '''Class Factory.

    Create class inheriting from flask_restful.Resource,
    bind them with theirs correspondings models classes.
    '''
    mapping['Model'] = model
    return type(name, (Resource,), mapping)


def register_api(app):
    '''Add Resources routes to the application.'''

    api = Api(app)
    item_mapping = {'get': _get, 'put': _put, 'delete': _delete}
    list_mapping = {'get': _get_all, 'post': _post}

    # Tags endpoints
    api.add_resource(factory('Tag', Tag, item_mapping), '/tag/<object_id>')
    api.add_resource(factory('TagList', Tag,  list_mapping), '/tag')

    # Feeds endpoints
    api.add_resource(factory('Feed', Feed, item_mapping), '/feed/<object_id>')
    api.add_resource(factory('FeedList', Feed, list_mapping), '/feed')

    #content endpoints
    api.add_resource(factory('Content', Content, {'get': _get}),
                  '/content/<object_id>')
    api.add_resource(factory('ContentList', Content, {'get': _get_all}), '/content')

