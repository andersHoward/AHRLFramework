"""Grid.py: grid class and utility methods to handle 2D grid arrays."""

# I'm using numpy because the internet neckbeards yell a
# lot about not using lists when you really want a matrix.
import numpy
from math import fabs
from .. import Constants as Const


class Grid(object):
    """Grid class: a 2D array with methods to manipulate sets of cells."""

    def __init__(self):
        """Grid init."""
        pass

    def create_grid(self):
        """Create and return a new numpy array grid."""
        new_grid = numpy.full((Const.MAP_WIDTH, Const.MAP_HEIGHT),
                              Const.ETerrainFlags.NONE)
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

    def get_manhattan_distance(self, point_1, point_2, terrain_flags_grid):
        """Also known as the taxi-cab, city block, chess , or rectilinear distance. So-called because it measures the
            distance between two points in terms of right-angled units(say for example, a 2D grid). Ignores all terrain
            features. Yes, I know I could have pulled an implementation of this from scipy or wherever, but that
            wouldn't learn me much, would it?

            Keyword arguments:
                point_1 -- a point on the grid.
                point_2 -- another point on the grid.
        """
        manhattan_distance = abs(point_1[0] - point_2[0]) + abs(point_1[1] - point_2[1])
        return manhattan_distance

        pass

    def get_bresenham_line_of_sight(self, grid, point_1, point_2):
        """TODO. Probably just a simple libtcod call."""
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
