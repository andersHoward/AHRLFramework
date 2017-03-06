"""Component.py: Module containing Component class."""

import json
from collections import OrderedDict as dict


class Component(object):
    '''Abstract base class for individual ECS component implementations.

    TODO:
        Component Factory.
        Component pool.
    '''

    __slots__ = ['defaults', 'owner_entity']
    defaults = {}
    Catalog = dict()
    ComponentTypes = dict()

    def __new__(cls, owner_entity=None, **properties):
        '''Pre-init, Registers catalog of E-C relationships.'''
        cname = cls.__name__
        # Check if this component class in ComponentTypes list;
        # register if not.
        if cname not in Component.ComponentTypes:
            Component.ComponentTypes[cname] = cls
            cls.Catalog = dict()
        # Check if owning entity in this component sub-class's catalog;
        # register if not.
        if owner_entity not in cls.Catalog:
            component = super(Component, cls).__new__(cls, entity=owner_entity, **properties)
        else:
            component = cls.Catalog(owner_entity)
        return component

    # TODO Add more with system

    def __init__(self, owner_entity=None, **properties):
        '''Component init.'''
        self.owner_entity = owner_entity

        # Go through defaults. Any properties sent it that are in the default{}
        # are set for this instance of the class, else use the default.
        for prop, val in self.defaults.iteritems():
            setattr(self, prop, properties.get(prop, val))

    def __repr__(self):
        '''<Component entity_id>.

        '''
        owner_entity_name =''
        class_name = self.__class__.__name__
        if self.owner_entity:
            # Iterate through all components on owner. If one of them matches
            # the name of the inst of this class, return repr string.
            for prop_name, component in self.owner_entity.components.iteritems():
                        if component == self:
                            owner_entity_name = ' entity: {}.{}'.format(self.owner_entity.name, prop_name)
                            break
        return '<{}{}>'.format(class_name, owner_entity_name)

    def __str__(self):
        '''Print to dump JSON of the properties.'''
        keys = self.defaults.keys()
        data = dict()
        for key in keys:
            if key != 'defaults':
                data[key] = getattr(self, key)
        json_string = '\n'.join(
            line.rstrip()
            for line in json.dump(data, indent=4).split('\n')
        )
        return json_string

    def __getitem__(self, key):
        '''Dunderdunder getitem allows access to attrs as dictionaries.'''
        return getattr(self, key)

    def __setitem__(self, key, value):
        '''Dunderdunder set item allows access to attrs as dictionaries.'''
        return setattr(self, key, value)

    def __eq__(self):
        '''Determine if self is equal to other.'''
        pass

    def restart(self):
        '''Set all component properties back to defaults.'''
        for prop_name, value in self.defaults.iteritems():
            setattr(self, prop_name, value)

if __name__ == '__main__':
    from doctest import testmod

    testmod()
