#  _____      _   _ _
# |  ___|    | | (_) |
# | |__ _ __ | |_ _| |_ _   _
# |  __| '_ \| __| | __| | | |
# | |__| | | | |_| | |_| |_| |
# \____/_| |_|\__|_|\__|\__, |
#                        __/ |
#                       |___/
#
# Abstract base class for a basic Entity, I.e. a generic object: the player, monsters, items, stairs.
# Is composed of Components.
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# CLASS DEFINITION: ENTITY ---
#
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class Entity():
    '''Abstract base class for a generic Entity.'''
    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None,equipment=None, always_visible = False):
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.always_visible = always_visible

        # Let the components of this object know who the parent object is.
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        self.item = item
        if self.item:
            self.item.owner = self
        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self
            self.item = Item()
            self.item.owner = self                                                                                      # There must be an Item component for the Equipment component to work properly

    # Move by the given amount.
    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):                                                                    # Check if the tile we're trying to move into is a blocking tile or contains a blocking object.
            self.x += dx
            self.y += dy

    # Moves object towards a target location. Normally used for simple AI.
    def move_towards(self, target_x, target_y):
        # Get vector.
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy **2)

        # Normalize to a unit vector (of 1), then round to int so movement is restricted to the grid, then move.
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # FUNCTION DEF: GET EQUIPPED IN SLOT --- Takes a slot as input and tells you what is equipped in that slot.
    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Returns the equipment in a slot, or None if it is empty.
    def get_equipped_in_slot(slot):
        for obj in inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None

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

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: PLAYER MOVE OR ATTACK --- interprets player movement as a move or an attack on an object.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def player_move_or_attack(dx, dy):
    global fov_recompute

    # Coordinates the player is trying to act upon.
    x = player.x + dx
    y = player.y + dy

    # Try to find attackable object at target tile.
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    # Attack if object found, else move
    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True