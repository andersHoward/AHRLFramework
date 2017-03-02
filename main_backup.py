import libtcodpy as libtcod
import math
import textwrap
import shelve

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# TOP-LEVEL VARIABLE DEFINITIONS
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Actual size of the window.
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

# GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50

# Map attributes
DEUB_MODE = False
MAP_WIDTH = 80
MAP_HEIGHT = 45
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
FOV_ALGO = 1
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 30

# Spells
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25

# Experience and leveling
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

# Color Defs
color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# CLASS DEFINITION: Tile --- A tile of the map and its properties
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Tile:
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False

        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# CLASS DEFINITION: Rect --- A rectangle on the map; used to characterize a room.
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        return(self.x1 <= other.x2 and self.x2 >= other.x1 and
               self.y1 <= other.y2 and self.y2 >= other.y1)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# CLASS DEFINITION: Object --- A generic object: the player, monsters, items, stairs. Always represented by an ascii character on-screen.
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class Object:
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
# COMPONENT CLASS DEF: FIGHTER --- Component that adds combat properties and methods to a base object instance.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Fighter:
    def __init__(self, hp, defense, power, xp, death_function=None):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.death_function = death_function

    # PROPERTIES
    # E.g. When player.power is accessed, this function is called instead of accessing the property directly.
    #   This allows us to sum the bonuses from all equipped items and buffs at run time, rather than having items and
    #   buffs modifying the player stat directly which can easily cause bugs.

    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_power + bonus

    @property
    def defense(self):  # return actual defense, by summing up the bonuses from all equipped items
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
        return self.base_defense + bonus

    @property
    def max_hp(self):  # return actual max_hp, by summing up the bonuses from all equipped items
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus

    # Make a target take damage.
    def attack(self, target):
        damage = self.power - target.fighter.defense

        if damage > 0:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage

        # Check for death and call death function.
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)

        # Award XP.
        if self.owner != player:
            player.fighter.xp += self.xp

    def heal(self, amount):

        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# COMPONENT CLASS DEF: BASICMONSTER --- Component that adds basic AI routines to an object instance.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class BasicMonster:
    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):                                                         # Monster sees you if you see it. TODO something better?

            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)

            # Close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# COMPONENT CLASS DEF: CONFUSEDMONSTER --- AI for a temporarily confused monster (reverts to previous AI after a while).
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class ConfusedMonster:
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    # Move randomly if still confused, else revert back to normal AI.
    def take_turn(self):
        if self.num_turns > 0:  # still confused...
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1

        else:
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# COMPONENT CLASS DEF: ITEM --- Component that allows an object to be picked up and used.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Item:
    def __init__(self, use_function=None):
        self.use_function = use_function

    # Add to the player's inventory and remove from the map
    def pick_up(self):

        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)

            # Special case: automatically equip, if the corresponding equipment slot is unused and the picked-up item
            #               is equippable.
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()

    # Equip an item or call its use function.
    def use(self):
        # If the object has an Equipment component, it can be equipped.
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        # Else just call the use function if it is defined.
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  # destroy after use, unless it was cancelled for some reason

    # Add to the map and remove from the player's inventory. also, place it at the player's coordinates
    def drop(self):
        # Special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()

        # add to the map and remove from the player's inventory. also, place it at the player's coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# COMPONENT CLASS DEF: EQUIPMENT --- Component that allows an object to be equipped to yield bonuses.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Equipment:
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.slot = slot
        self.is_equipped = False

    # Toggle don/doff status.
    def toggle_equip(self):
        if self.is_equipped:
            self.doff()
        else:
            self.equip()

    # Equip object.
    def equip(self):
        # If the slot is already being used, doff whatever is there first
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.doff()

        self.is_equipped = True
        message('Equipped ' + self.owner.name + 'on ' + self.slot + '.', libtcod.light_green)

    # Doff object.
    def doff(self):
        if not self.is_equipped: return
        self.is_equipped = False
        message('Doffed ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)

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

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: CREATE ROOM --- Take a Rectangle and make all of its tiles passable.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def create_room(room):
    global map

    # Iterate through tiles in a placed room (i.e. a Rect()), and make them passable.
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: CREATE HORIZONTAL TUNNEL --- Does what it says on the tin.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def create_h_tunnel(x1, x2, y):
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: CREATE VERTICAL TUNNEL --- Does what it says on the tin.
# ///////v///////////////////////////////////////////////////////////////////////////////////////////////////////////////
def create_v_tunnel(y1, y2, x):
    global map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: MAKE MAP
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def make_map():                                                                                                         # Nested List Comprehension to fill the map with "unblocked" tiles.
    global map, player, objects, stairs                                                                                 # One very important piece of advice: in list comprehensions, always call the constructor of the objects you're creating, like we did with Tile(False). If we had tried to first create an unblocked tile like floor = Tile(False) and then in the list comprehension just refer to that same floor, we'd get all sorts of weird bugs! That's because all elements in the list would point to the exact same Tile (the one you defined as floor), not copies of it. Changing a property of one element would appear to change it in other elements as well!
    objects = [player]

    # First, fill map with blocked tiles.
    map = [[Tile(True)
            for y in range(MAP_HEIGHT)]
           for x in range(MAP_WIDTH)]

    # Generate a random number of randomly sized rooms out of our solid world.
    rooms = []
    num_rooms = 0

    # Randomize the params of a room.
    for r in range(MAX_ROOMS):
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        # Create a Rect with the randomized attributes.
        new_room = Rect(x, y, w, h)

        # Check our new room against all existing rooms for overlap.
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        # Room is valid; carve it out of the solid world.
        if not failed:
            create_room(new_room)
            (new_x, new_y) = new_room.center()

            # DEBUG MODE: print "room number" to see how the map drawing worked
            if DEUB_MODE == True:
                room_no = Object(new_x, new_y, chr(65 + num_rooms), 'room number', libtcod.white)
                objects.insert(0, room_no)  # draw early, so monsters are drawn on top

            # Start player in first room.
            if num_rooms == 0:
                player.x = new_x
                player.y = new_y
            else:                                                                                                               # All rooms after the first must be connected via a tunnel that we create here.
                # Get the centerpoint of the previous room. We'll use that as our connection target.
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                # Flip a coin to determine the connecting hall's directionality.
                if libtcod.random_get_int(0, 0, 1) == 1:
                    # first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    # first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

        # Add some contents to this room, such as monsters
        place_objects(new_room)

        # Finally, append the new room to the list
        rooms.append(new_room)
        num_rooms += 1

    # Create stairs at the center of the last room
    stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white, True)
    objects.append(stairs)
    stairs.send_to_back()  # so it's drawn below the monsters

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

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: PLACE OBJECTS --- Takes a room and places randomized objects in it.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def place_objects(room):
    # CREATE TABLES FOR OBJECT ROLL CHANCES, AND THEIR CHANCE ADVANCEMENTS TO PASS TO from_dungeon_level().
    # Maximum number of monsters per room
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])

    # Chance of each monster
    monster_chances = {}
    monster_chances['orc'] = 80  # orc always shows up, even if all other monsters have 0 chance
    monster_chances['troll'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])

    # Maximum number of items per room
    max_items = from_dungeon_level([[1, 1], [2, 4]])

    # Chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}
    item_chances['heal'] = 35  # healing potion always shows up, even if all other items have 0 chance
    item_chances['lightning'] =     from_dungeon_level([[25, 4]])
    item_chances['fireball'] =      from_dungeon_level([[25, 6]])
    item_chances['confuse'] =       from_dungeon_level([[10, 2]])
    item_chances['sword'] =         from_dungeon_level([[5, 4]])
    item_chances['shield'] =        from_dungeon_level([[15, 8]])

    # Choose random number of monsters.
    num_monsters = libtcod.random_get_int(0,0,max_monsters)

    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1, room.x2)
        y = libtcod.random_get_int(0, room.y1, room.y2)

        # If the random location is not blocked, go ahead and create the monster object.
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)
            if choice == 'orc':                                                                   # 80% chance of getting an orc, else troll.
                fighter_component = Fighter(hp=20, defense=0, power=4, xp=35,death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x,y,'o', 'orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)
            elif choice == 'troll':
                fighter_component = Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True,fighter=fighter_component, ai=ai_component)

            # Finally, append the valid monster to the objects list.
            objects.append(monster)

    # Choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_items)

    # Distribute random items in random (unblocked) locations.
    for i in range(num_items):
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'heal':
                # Create a healing potion
                item_component = Item(use_function=cast_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)
            elif choice == 'lightning':
                # Create lightning bolt scroll.
                item_component = Item(use_function=cast_lightning)
            elif choice == 'fireball':
                # Create a fireball scroll.
                item_component = Item(use_function=cast_fireball)
                item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)
            elif choice == 'confuse':
                # Create a confuse scroll
                item_component= Item(use_function=cast_confuse)
                item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)
            elif choice == 'sword':
                # create a sword
                equipment_component = Equipment(slot='right hand', power_bonus=3)
                item = Object(x, y, '/', 'sword', libtcod.sky, equipment=equipment_component)
            elif choice == 'shield':
                # create a shield
                equipment_component = Equipment(slot='left hand', defense_bonus=1)
                item = Object(x, y, '[', 'shield', libtcod.darker_orange, equipment=equipment_component)

            objects.append(item)
            item.send_to_back()                                                                                         # Items appear below other objects
            item.always_visible = True                                                                                  # Items remain visible even out of FOV if in an explored area.

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: BLOCKS --- Tests whether a tile at a given position is a blocking tile or contains a blocking object.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def is_blocked(x, y):
    if map[x][y].blocked:
        return True

    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return  True

    return False

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: RENDER BAR --- Render a generic bar (HP, experience, etc). first calculate the width of the bar
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    # Render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # Now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # Finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
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
# FUNCTION DEF: RENDER ALL
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute

    # Recompute FOV if necessary, then draw tiles based on their current visibility to the player.
    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
        for y in range(MAP_HEIGHT):                                                                                     # Draw all tiles in the map.
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)                                                          # Check visibility of this tile.
                wall = map[x][y].block_sight
                if not visible:                                                                                         # Tile out of player FOV.
                    # If it's not visible right now, the player can only see it if it's explored
                    if map[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:                                                                                                   # Tile IN player FOV.
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET)

                        # Since it's visible, explore it.
                        map[x][y].explored = True

    # Draw all objects in the object list, but draw the player last on top of everything.
    for object in objects:
        if object != player:
            object.draw()
    player.draw()

    # Blit the contents of "con" to the root console.
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)                                               # Blit from the buffer console to the base console from the origin pixel to the max screen size.

    # Prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # Print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    # Show the player's stats.
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)

    # Print current dungeon level/location.
    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))

    # display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    # blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: MESSAGE --- Formats a string and manages the message log.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def message(new_msg, color=libtcod.white):
    # split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        # if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        # add the new line as a tuple, with the text and the color
        game_msgs.append((line, color))

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

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: MENU --- a generic menu GUI.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    # print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    # Special Case: toggle fullscreen
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    # convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: INVENTORY MENU --- # show a menu with each item of the inventory as an option
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def inventory_menu(header):
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            # Show additional information, in case it's equipped.
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)

    # if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: MESSAGE BOX --- Use a menu() as a sort of "message box."
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def msgbox(text, width=50):
    menu(text, [], width)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: KEY HANDLING
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def handle_keys():
    global key

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  # exit game

    if game_state == 'playing':
        # Movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)
        elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)
        elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1, -1)
        elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)
        elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1, 1)
        elif key.vk == libtcod.KEY_KP5:
            pass  # Do nothing ie wait for the monster to come to you

        else:
            # Test for other keys
            key_char = chr(key.c)

            if key_char == 'c':
                # Show character information
                level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                msgbox(
                    'Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(player.fighter.max_hp) +
                    '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' + str(player.fighter.defense),
                    CHARACTER_SCREEN_WIDTH)

            if key_char == 'g':
                # Pick up an item
                for object in objects:  # look for an item in the player's tile
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break

            if key_char == 'i':
                # Show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'd':
                # Show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if key_char == '<':
                # Go down stairs, if the player is on them
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()

            return 'didnt-take-turn'

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: CHECK LEVEL UP - See ifm player has gained enough XP to level up.
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def check_level_up():
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        player.level += 1
        player.fighter.xp -= level_up_xp
        message('Your skills grow stronger. You reached level ' + str(player.level) + '!', libtcod.yellow)

        # Ask for a skill advancement choice until one is made.
        choice = None
        while choice == None:
            choice = menu('Level up! Choose a stat to raise:\n',
                          ['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
                           'Strength (+1 attack, from ' + str(player.fighter.power) + ')',
                           'Agility (+1 defense, from ' + str(player.fighter.defense) + ')'], LEVEL_SCREEN_WIDTH)

        if choice == 0:
            player.fighter.base_max_hp += 20
            player.fighter.hp += 20
        elif choice == 1:
            player.fighter.base_power += 1
        elif choice == 2:
            player.fighter.base_defense += 1

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: MONSTER DEATH HANDLING
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def player_death(player):
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'
    player.char = '%'
    player.color = libtcod.dark_red

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: MONSTER DEATH HANDLING --- Transform it into a corpse and cleanup its components.
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def monster_death(monster):
    message('The ' + monster.name + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points.',
            libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()                                                                                              # Ensures that all other objects draw on top of this monster's corpse.

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: CAST HEAL --- A basic spell definition.
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def cast_heal():
    # heal the player
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'

    message('Your wounds start to feel better!', libtcod.light_violet)
    player.fighter.heal(HEAL_AMOUNT)

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: CAST LIGHTNING --- A basic spell definition.
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def cast_lightning():
    # Find the nearest enemy within max range and damage it.
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:
        message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'

    # Zap it!
    message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
            + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: CAST CONFUSE --- A basic spell definition.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def cast_confuse():
    # Ask the player for a target to confuse
    message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None: return 'cancelled'

    # Else replace the nearest monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  # tell the new component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!',
            libtcod.light_green)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: CAST FIREBALL --- A basic spell definition.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def cast_fireball():
    # Ask the player for a target tile to throw a fireball at
    message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)

    for obj in objects:  # damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE)

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

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: NEW GAME --- Initialize all of the variables required for a new game.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level

    # Set up a new game: create Player object and map.
    fighter_component = Fighter(hp=100, defense=1, power=4, xp=0, death_function=player_death)
    player = Object(0, 0, '@', 'player', libtcod.white, blocks = True, fighter=fighter_component)

    player.level = 1

    # Generate a map and FOV map(at this point, it is not drawn to the screen).
    dungeon_level = 1
    make_map()
    initialize_fov()

    game_state = 'playing'
    inventory = []

    # Create the list of game messages and their colors. Starts empty.
    game_msgs = []
    message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)

    # Initial equipment: a dagger
    equipment_component = Equipment(slot='right hand', power_bonus=2)
    obj = Object(0, 0, '-', 'dagger', libtcod.sky, equipment=equipment_component)
    inventory.append(obj)
    equipment_component.equip()
    obj.always_visible = True

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: INITIALIZE_FOV --- Initialize the FOV map.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True

    # Create the FOV map: create a duplicate (but inverse) FOV map according to the generated game map.
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

    # Unexplored areas start black (which is the default background color)
    libtcod.console_clear(con)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: NEXT LEVEL --- Advances to next floor of the dungeon.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def next_level():
    global dungeon_level
    # Heal the player by 50%
    message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)

    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    dungeon_level += 1
    make_map()                                                                                                          # Create a fresh new level!
    initialize_fov()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: SAVE GAME --- Save the game state by shelving, which recursively saves every object referenced by the
#                                shelved objects.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def save_game():
    file = shelve.open('savegame', 'n')                                                                                 # Open a new empty shelve (possibly overwriting an old one) to write the game data
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player)                                                                        # Index of player object WITHIN the objects list. If we had directly referenced the 'player' object, we would end up with two instances of 'player' copied b/c one already existed in the 'objects' list!
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['stairs_index'] = objects.index(stairs)
    file['dungeon_level'] = dungeon_level
    file.close()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: LOAD GAME --- Unshelve our game state into our previously named global variables.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def load_game():
    global map, objects, player, inventory, game_msgs, game_state

    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]  # get index of player in objects list and access it
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    stairs = objects[file['stairs_index']]
    dungeon_level = file['dungeon_level']
    file.close()

    initialize_fov()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: PLAY GAME --- The main game loop.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def play_game():
    global key, mouse
    player_action = None
    mouse = libtcod.Mouse()
    key = libtcod.Key()

    while not libtcod.console_is_window_closed():
        # Render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()
        libtcod.console_flush()                                                                                         # At the end of the main loop, you must present all changes to the screen. This is called Flushing.

        # Check for level up before anything else because if level up, we have to render the level up menu before all else.
        check_level_up()

        # Erase all objects at their old locations before they move.
        for object in objects:
            object.clear()

        # Handle keys and exit game if needed
        player_action = handle_keys()                                                                                   # Break main game loop once we have an acceptable input.
        if player_action == 'exit':
            save_game()                                                                                                 # Save game state when exiting.
            break

        # After player takes turn, NPCs take turn.
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: MAIN MENU --- the Main Menu.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
if __name__ == '__main__':
    def main_menu():
        img = libtcod.image_load('menu_background1.png')

        while not libtcod.console_is_window_closed():
            # Show the background image at twice the normal console resolution
            libtcod.image_blit_2x(img, 0, 0, 0)

            # show the game's title, and some credits!
            libtcod.console_set_default_foreground(0, libtcod.light_yellow)
            libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 4, libtcod.BKGND_NONE, libtcod.CENTER,
                                     'SOME FUCKING GAME')
            libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER,
                                     'By SOME FUCKING DUDES')

            # Show options and wait for the player's choice.
            choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
            if choice == 0:
                new_game()
                play_game()
            if choice == 1:
                try:
                    load_game()
                except:
                    msgbox('\n No saved game to load.\n', 24)
                    continue
                play_game()
            elif choice == 2:
                break

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# INITIALIZE AND MAIN LOOP
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# System Init: Initialize console(s)
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "python/AH RL Framework", False)                                 # Initialize the default (base) console. This is where we will blit all graphics to.
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)                                                                  # Initialize another console to act as a buffer.
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

main_menu()                                                                                                             # Load the Main Menu to begin the game!