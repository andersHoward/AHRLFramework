#  _____ _____ _      _____
# |_   _|_   _| |    |  ___|
#   | |   | | | |    | |__
#   | |   | | | |    |  __|
#   | |  _| |_| |____| |___
#   \_/  \___/\_____/\____/
#
# The base class for map tiles and the properties they can hold.
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Tile:
    '''A tile of the map and its properties.'''
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False

        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight