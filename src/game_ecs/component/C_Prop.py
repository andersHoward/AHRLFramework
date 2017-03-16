import yaml
from .. import GameComponent

class C_Prop(GameComponent, yaml.YAMLObject):
    '''Component that holds props that can be held by Tiles.'''
    yaml_tag = u'!C_Prop'

    def __init__(self, blocks, blocks_sight=None, appropriate_terrains=None, prop_interaction_type=None):
        self._blocks = blocks
        self._blocks_sight = blocks_sight
        self._appropriate_terrains = []
        self._appropriate_terrains = appropriate_terrains

    @property
    def blocks_sight(self):
        return self._blocks_sight

    @property
    def blocks(self):
        return self._blocks

    @property
    def _appropriate_terrains(self):
        return self._appropriate_terrains
