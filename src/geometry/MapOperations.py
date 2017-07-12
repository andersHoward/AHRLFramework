'''Map Geo Operations: generic utility and geometry methods for grids (which may or may not be game level maps).'''

# I'm using numpy because the internet yells about how it's more efficient than a Python list for 2D matrices.
import numpy

from .. import Constants as Const


def create_grid(self):
    """Create and return a new numpy array grid. These are generic grids meant to hold additional cell properties
        beyond the default libtcod properties (visibility, walkability, transparency). I.e. this is a defacto extension
        of libtcod's Map object, allowing each element to hold Cell entities.
    """

    # TODO Don't populate a new grid with terrain flags by default. Init each cell w/ an empty entity.
    new_grid = numpy.full((Const.MAP_WIDTH, Const.MAP_HEIGHT), Const.ETerrainFlags.NONE)
    return new_grid


def copy_to_new_grid(self, grid_copy_source):
    """Copy one grid to a new grid instance."""
    return_grid = self.create_grid()
    return_grid = self.copy_grid_to_grid(grid_copy_source, return_grid)
    return return_grid


def copy_grid_to_grid(self, grid_copy_source, grid_paste_destination):
    """Copy from one specified grid to another."""
    for x in grid_copy_source:
        for y in grid_copy_source:
            grid_paste_destination([x, y])
    return grid_paste_destination

def get_chebyshev_distance(self, grid, point_1, point_2):
    """TODO."""
    pass

def get_dijkstra_path(self, grid, point_1, point_2):
    """TODO."""
    pass

def fill_entire_grid(self, grid_to_fill, value_to_fill_with):
    """TODO."""
    pass

def find_replace_value_on_grid(self, value_to_find, new_value):
    """TODO."""
    pass

def draw_shape_primitive_on_grid(self, grid, shape, origin_position):
    """TODO. Should take a shape type from const enum; call into geo.py."""
    pass

def draw_cellular_automata_on_grid(self, grid, generation_rounds,
                                   birth_parameters, death_parameters,
                                   width_min, width_max, height_min,
                                   height_max):
    """TODO: use a cellular automata step func until gen rounds."""
    pass

def place_tunnelers_on_grid(self, grid, number_of_tunnelers):
    """TODO Tunnelers re: Kyzrati and DungeonMaker."""
    pass

def do_grid_set_operation(self, grid, operation):
    """TODO. Union, intersect, sub, invert."""
    pass

def get_terrain_grid(self, grid):
    """TODO. Union, intersect, sub, invert."""
    pass

def get_winding_way(self, grid, point_1, point_2):
    """TODO: Not sure how to get this to fit in with other generators. Intent: maze algo by Rob Nystom."""
    pass

def get_least_costly_cell(self, grid):
    """TODO."""
    pass

def get_random_valid_location(self, grid):
    """TODO: check if any valid locations in grid, then get one."""
    pass

def fill_marked_grid_location(self, grid, fill_marker_value, replacement_value):
    """TODO. Takes a value that represents another function 'marking' cells, then replaces the value.
        E.g. Algo decides 'grass goes here' and marks it? Review Brogue.
    """
    pass

def get_manhattan_distance(self, point_1, point_2):
    """Simple distance measurer that measures cell distance in right-angle turns.

        AKA "Taxi Cab Distance", "Rectilinear Distance" and others.
        Measures the distance between two points (cells), but only moving
        orthoganally, never diagonally.

        Keyword arguments:
            point_1 -- a point on the grid.
            point_2 -- another point on the grid.

        TODO:
            -Make this play nice with terrain when that comes in.
    """
    manhattan_distance = abs(point_1[0] - point_2[0]) + abs(point_1[1] - point_2[1])
    return manhattan_distance
