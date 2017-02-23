import libtcodpy as libtcod
import math
import textwrap

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
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2
FOV_ALGO = 1
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

# Spells
HEAL_AMOUNT = 4
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 12

# Color Defs
color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

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
# CLASS DEFINITION: Tile --- A tile of the map and its properties
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Tile:
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False

        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# CLASS DEFINITION: Object --- A generic object: the player, monsters, items, stairs. Always represented by an ascii character on-screen.
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class Object:
    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None):
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color

        # Let the components of this object know who the parent object is.
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        self.item = item
        if self.item:  # let the Item component know who owns it
            self.item.owner = self

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

    # If object is in FOV, set the color and then draw the character that represents this item at its current position.
    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
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
    def __init__(self, hp, defense, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function

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

    # Just call the "use_function" if it is defined
    def use(self):

        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  # destroy after use, unless it was cancelled for some reason

    # Add to the map and remove from the player's inventory. also, place it at the player's coordinates
    def drop(self):
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: CREATE ROOM --- Take a Rectangle and make all of its tiles passable.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def create_room(room):
    global map

    # Carve out a room.
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
    global map, player                                                                                                  # One very important piece of advice: in list comprehensions, always call the constructor of the objects you're creating, like we did with Tile(False). If we had tried to first create an unblocked tile like floor = Tile(False) and then in the list comprehension just refer to that same floor, we'd get all sorts of weird bugs! That's because all elements in the list would point to the exact same Tile (the one you defined as floor), not copies of it. Changing a property of one element would appear to change it in other elements as well!

    # Make a hunk of solid rock.
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



# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: PLACE OBJECTS --- Takes a room and places an object in it.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def place_objects(room):
    # Choose a random number of monsters and place them in random spots in the room.
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1, room.x2)
        y = libtcod.random_get_int(0, room.y1, room.y2)

        # If the random location is not blocked, go ahead and create the monster object.
        if not is_blocked(x, y):
            if libtcod.random_get_int(0,0,100) < 80:                                                                            # 80% chance of getting an orc, else troll.
                fighter_component = Fighter(hp=10, defense=0, power=3, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x,y,'o', 'orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)
            else:
                fighter_component = Fighter(hp=16, defense=1, power=4, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True,fighter=fighter_component, ai=ai_component)

            # Finally, append the valid monster to the objects list.
            objects.append(monster)

    # Choose random number of items
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)
    # Distribute random items in random (unblocked) locations.
    for i in range(num_items):
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        if not is_blocked(x, y):
            dice =  libtcod.random_get_int(0, 0, 100)
            if dice < 70:
                # Create a healing potion
                item_component = Item(use_function=cast_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)
            elif dice < 70+10:
                # Create lightning bolt scroll.
                item_component = Item(use_function=cast_lightning)
            elif dice < 70+10+10:
                # Create a fireball scroll.
                item_component = Item(use_function=cast_fireball)
                item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)
            else:
                # Create a confuse scroll
                item_component= Item(use_function=cast_confuse)
                item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)

                objects.append(item)
                item.send_to_back()                                                                                     # Items appear below other objects

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
        options = [item.name for item in inventory]

    index = menu(header, options, INVENTORY_WIDTH)

    # if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: KEY HANDLING
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def handle_keys():
    global key;

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  # exit game

    if game_state == 'playing':
        # Movement keys
        if key.vk == libtcod.KEY_UP:
            player_move_or_attack(0, -1)

        elif key.vk == libtcod.KEY_DOWN:
            player_move_or_attack(0, 1)

        elif key.vk == libtcod.KEY_LEFT:
            player_move_or_attack(-1, 0)

        elif key.vk == libtcod.KEY_RIGHT:
            player_move_or_attack(1, 0)
        else:
            # Test for other keys
            key_char = chr(key.c)

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

            return 'didnt-take-turn'

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
    message(monster.name.capitalize() + ' is dead!', libtcod.orange)
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
# INITIALIZE AND MAIN LOOP
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Init console(s)
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "python/AH RL Framework", False)                                 # Initialize the default (base) console. This is where we will blit all graphics to.
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)                                                                  # Initialize another console to act as a buffer.
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

# Create Player object and put it into the objects list.
fighter_component = Fighter(hp=30, defense=2, power=5, death_function=player_death)
player = Object(0, 0, '@', 'player', libtcod.white, blocks = True, fighter=fighter_component)
objects = [player]

# Create map before the game begins.
make_map()

# Create the FOV map, according to the generated game map.
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

fov_recompute = True
game_state = 'playing'
player_action = None
inventory = []
game_msgs = []
message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)
mouse = libtcod.Mouse()
key = libtcod.Key()

#################################
# MAIN LOOP
#################################
while not libtcod.console_is_window_closed():

    # Render the screen
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
    render_all()
    libtcod.console_flush()                                                                                             # At the end of the main loop, you must present all changes to the screen. This is called Flushing.

    # Erase all objects at their old locations before they move.
    for object in objects:
        object.clear()

    # Handle keys and exit game if needed
    player_action = handle_keys()                                                                                           # Break main game loop once we have an acceptable input.
    if player_action == 'exit':
        break

    # After player takes turn, NPCs take turn.
    if game_state == 'playing' and player_action != 'didnt-take-turn':
        for object in objects:
            if object.ai:
                object.ai.take_turn()