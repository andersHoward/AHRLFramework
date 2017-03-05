#  _____      _   _ _
# |  ___|    | | (_) |
# | |__ _ __ | |_ _| |_ _   _
# |  __| '_ \| __| | __| | | |
# | |__| | | | |_| | |_| |_| |
# \____/_| |_|\__|_|\__|\__, |
#                        __/ |
#                       |___/
#
"""Module that contains abstract base class for a basic Entity,
Is composed of Components."""

import libtcodpy


class Entity():
    '''Abstract base class for a generic Entity.
        Args:
            x (int): initial
        '''
    def __init__(self, components):
        pass


    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # FUNCTION DEF: GET ALL EQUIPPED --- Takes an object and returns a list of all items equipped on that object.
    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Returns the equipment in a slot, or None if it is empty.
    def get_all_equipped(obj):
        if obj == player:
            equipped_list = []
            for item in inventory:
                if item.equipment and item.equipment.is_equipped:
                    equipped_list.append(item.equipment)
            return equipped_list
        else:
            return []  # Other objects have no equipment (at this point)

    # Return dist to another object. TODO this should be in a generic utils module.
    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    # Return the distance to some coordinates
    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    # If object is in FOV OR as been explored and is set to "always visible", set the color and then draw the character
    # that represents this item at its current position.
    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y) or (self.always_visible and map[self.x][self.y].explored):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    # Moves this object to the back of the objects list. Useful for affecting draw order.
    def send_to_back(self):
        global objects
        objects.remove(self)
        objects.insert(0, self)

    # Erase the character that represents this object.
    def clear(self):
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
