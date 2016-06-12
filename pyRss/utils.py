# coding: utf-8

from flask_restful import reqparse

def get_feed_parser():
    '''Return a request parser ready to validate feed objects'''
    parser = reqparse.RequestParser()
    for item in ['source', 'name']:
        parser.add_argument(name=item, type=str, required=True)
    parser.add_argument('tags', type=str, action='append', required=True)
    return parser

def get_tag_parser():
    '''Return a request parser ready to validate tag objects'''
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True)
    return parser

