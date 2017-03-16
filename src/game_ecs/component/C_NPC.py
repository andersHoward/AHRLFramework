import yaml
from .. import GameComponent

class C_NPC(GameComponent, yaml.YAMLObject):
    """Component that holds NPC data."""
    yaml_tag = u'!C_NPC'

    def __init__(self):
        pass
