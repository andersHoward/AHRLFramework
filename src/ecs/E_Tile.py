#  _____ _____ _      _____
# |_   _|_   _| |    |  ___|
#   | |   | | | |    | |__
#   | |   | | | |    |  __|
#   | |  _| |_| |____| |___
#   \_/  \___/\_____/\____/
#
# The base class for map tiles and the properties they can hold.
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class E_Tile():
    '''A tile of the map and its properties.'''
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False

        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: IS BLOCKED?
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    def bIsBlocked(x, y):
        '''Tests whether a tile at a given position is a blocking tile or contains a blocking object.'''
        if map[x][y].blocked:
            return True

        for object in objects:
            if object.blocks and object.x == x and object.y == y:
                return True
        return False