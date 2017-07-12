"""Tile component extends libtcod's simple tile functionality."""

import yaml

from .. import GameComponent


class C_Tile(GameComponent, yaml.YAMLObject):
    """Component that holds tile properties.

    TODO:
        -Hold my terrain type, dijkstra cost of that type.
        -Dict of entities occupying my space and their types.
        -Dict of persistent effects occupying my space.
        -Yaml tag config. How do they work?
    """

    # Yaml tag. When this tag is parsed from the config file, it will send all
    # key/value pairs into this class's init constructor as arguments.
    # http://pyyaml.org/wiki/PyYAMLDocumentation#Tutorial
    yaml_tag = u'!C_Tile'

    def __init__(self, blocked, block_sight=None, terrain_type=None,
                 terrain_cost=None, occupying_entities=None,
                 persistent_effects=None):
        """C_Tile init method. Map gen determines starting attrs."""
        self.blocked = blocked
        self.explored = False

        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight
