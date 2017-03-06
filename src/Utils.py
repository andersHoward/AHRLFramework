# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: RANDOM CHOICE INDEX --- Choose one option from list of chances, returning its index
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def random_choice_index(chances):
    dice = libtcod.random_get_int(0, 1, sum(chances))

    # Go through all chances, keeping sum.
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
        # See if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: RANDOM CHOICE --- Alternative to random_choice_index using strings instead of indexes.
#                                   Choose one option from dictionary of chances, returning its key.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def random_choice(chances_dict):
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: FROM DUNGEON LEVEL-- returns a value that depends on dungeon level. the table specifies what value
#                                   occurs after each level, default is 0.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def from_dungeon_level(table):
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: GET NAMES UNDER MOUSE --- Get a list of moused-over object names
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def get_names_under_mouse():
    global mouse


    (x, y) = (mouse.cx, mouse.cy)

    # create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects
             if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]

    names = ', '.join(names)  # join the names, separated by commas
    return names.capitalize()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: CLOSEST MONSTER --- Returns closest enemy, up to a maximum range and in the player's FOV
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def closest_monster(max_range):
    closest_enemy = None
    closest_dist = max_range + 1                                                                                        # start with (slightly more than) maximum range

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            # Calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  # it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: TARGET TILE --- Return the position of a tile left-clicked in player's FOV (optionally in a range),
#                               or (None,None) if right-clicked.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def target_tile(max_range=None):
    global key, mouse
    while True:
        # Render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()                                                                                         # Flush the console to present changes to the player.
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)                          # Absorbs key presses and does nothing with them - this is a mouse interface, baby!
        render_all()

        (x, y) = (mouse.cx, mouse.cy)

        # Accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
                (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:                                                       # Cancel if the player right-clicked or pressed Escape
            return (None, None)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: TARGET MONSTER --- Returns a clicked monster inside FOV up to a range, or None if right-clicked
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def target_monster(max_range=None):
    while True:
        (x, y) = target_tile(max_range)
        if x is None:                                                                                                   # Player cancelled
            return None

        # Return the first clicked monster, otherwise continue looping
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj

# Return dist to another object. TODO this should be in a generic utils module.
def distance_to(self, other):
    dx = other.x - self.x
    dy = other.y - self.y
    return math.sqrt(dx ** 2 + dy ** 2)

# Return the distance to some coordinates
def distance(self, x, y):
    return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
