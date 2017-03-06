#!/usr/bin/env python

"""Entity.py: Module that contains abstract base class for a generic Entity"""

from collections import OrderedDict as dict
from uuid import uuid4


class Entity(object):
    '''Entity container for a UID and list of components.

    >>> e = Entity('player', 0)
    >>> e
    <Entity player:0>
    >>> print e
    OrderedDict()
    >>> e.health = 1
    >>> print e.health
    1
    >>> print e['health']
    1
    >>> e['health'] = 10
    >>> e.health
    10
    '''
    __slots__ = ['uid', 'name', 'components'] # Define the attributes that we expect this class to have with slot.

    def __init__(self, name=None, uid=None):
        '''Entity init.'''
        self.uid = uuid4() if uid is None else uid
        self.name = name if name is not None else ''
        self.components = dict()

    def __repr__(self):
        '''Querying the representation returns: <Entity name:0>.'''
        cname = self.__class__.__name__
        name = self.name or self.uid
        if name != self.uid:
            name = '{}:{}'.format(self.name, self.uid)
        return '<{} {}>'.format(cname, name)

    def __str__(self):
        '''Printing this class runs this to return component collection.'''
        return str(self.components)

    def __getitem__(self, key):
        '''Return the component value using the key.'''
        return self.components[key]

    def __setitem__(self, key, value):
        '''Set the component using the key and value.'''
        # TODO Component updates
        self.components[key] = value

    def __getattr__(self, key):
        '''Allows access to the properties/components as an attr.'''
        if key in super(Entity, self).__getattribute__('__slots__'):
            return super(Entity, self).__getattribute__(key)
        else:
            return self.components[key]

    def __setattr__(self, key, value):
        '''Allows access to the properties/components as an attr.'''
        if key in super(Entity, self).__getattribute__('__slots__'):
            super(Entity, self).__setattr__(key, value)
        else:
            self.components[key] = value

if __name__ == '__main__':
    from doctest import testmod

    testmod()
