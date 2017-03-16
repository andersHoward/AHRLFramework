from .. import GameSystem

class SYS_Tiles(GameSystem):
    """Operations for manipulating tile data."""
    def __init__(self, tile_matrix):
        global _current_map_tiles
        _current_map_tiles = tile_matrix

    def bIsBlocked(map, x, y):
        '''Tests whether a tile at a given position is a blocking tile or contains a blocking object.'''
        if map[x][y].blocked:
            return True

        for tile in _current_map_tiles:
            if tile.blocks and tile.x == x and tile.y == y:
                return True
        return False
