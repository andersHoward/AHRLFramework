import yaml
from .. import GameComponent

class C_Tile(GameComponent, yaml.YAMLObject):
    '''Component that holds tile properties.'''
    # Yaml tag. When this tag is parsed from the config file, it will send
    # all of the key/value pairs into this class's init constructor as arguments.
    # http://pyyaml.org/wiki/PyYAMLDocumentation#Tutorial
    yaml_tag = u'!C_Tile'

    def __init__(self, blocked, block_sight=None, terrain_type=None, persistent_effects=None):
        self.blocked = blocked
        self.explored = False

        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
