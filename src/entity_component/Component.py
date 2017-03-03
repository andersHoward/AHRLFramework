# /  __ \                                            | |
# | /  \/ ___  _ __ ___  _ __   ___  _ __   ___ _ __ | |
# | |    / _ \| '_ ` _ \| '_ \ / _ \| '_ \ / _ \ '_ \| __|
# | \__/\ (_) | | | | | | |_) | (_) | | | |  __/ | | | |_
#  \____/\___/|_| |_| |_| .__/ \___/|_| |_|\___|_| |_|\__|
#                       | |                            
#                       |_|
#
# Abstract base class for individual ECS component implementations.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#
#    ____ ____ _  _ ___  ____ _  _ ____ _  _ ___
#    |    |  | |\/| |__] |  | |\ | |___ |\ |  |
#    |___ |__| |  | |    |__| | \| |___ | \|  |
#
#       Component base class definition.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import json

class Component():
    '''The abstract base class for all individual ECS components.'''

    __slots__['defaults', 'entity']
    defaults = {}

    def __init__(self, entity, **properties):
        '''Properties'''
        self.owner = entity

    def __repr__(self):
        ''' <Component entity_id>'''

    def __str__(self):
        '''''' Dump JSON of the properties.'''

    def __eq__(self):
        '''Determines if self is equal to other.'''

    if __name__ == '__main__':
        from doctest import testmod

        testmod()
        print('Hello from Component!')