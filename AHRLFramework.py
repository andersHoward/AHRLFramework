import libtcodpy as libtcod
import math

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# TOP-LEVEL VARIABLE DEFINITIONS
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Map attributes
DEUB_MODE = True
MAP_WIDTH = 80
MAP_HEIGHT = 45
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 3
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

# Color Defs
color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

# Actual size of the window.
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

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
    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None):
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

    # Move by the given amount.
    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):                                                             # Check if the tile we're trying to move into is a blocking tile or contains a blocking object.
            self.x += dx
            self.y += dy

    # Moves object towards a target location. Normally used for simple AI.
    def move_towards(self, target_x, target_y):
        # Get vector.
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy **2)

        # Normalize to a unit vector (of 1), then round to int so movement is restricted to the grid.
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        # Finally, move the single grid space we've determined.
        self.move(dx, dy)

    # Return dist to another object. TODO this should be in a generic utils module.
    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    # If object is in FOV, set the color and then draw the character that represents this item at its current position.
    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    # Moves this object to the back of the objects list. Useful for affecting draw order.
    def send_to_back(self):
        global objects.remove(self)
        objects.insert(0, self)

    # Erase the character that represents this object.
    def clear(self):
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# COMPONENT CLASS DEF: FIGHTER --- Component that adds combat properties and methods to a base object instance.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Fighter:
    def __init__(self, hp, defense, power, death_function=None):
        self.death_function = death_function
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage

        # Check for death and call death function.
        if self.hp <= 0:
            function = self.death_function
            if function is not None
                function(self.owner)

    def attack(self, target):
        damage = self.power - target.fighter.defense

        if damage > 0:
            print self.owner.name.capitalize() + ' atttacks ' + target.name + ' for ' + str(damage) + ' hit points.'
        else:
            print self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!'


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
                fighter_component = Fighter(hp=10, defense=0, power=3)
                ai_component = BasicMonster()
                monster = Object(x,y,'o', 'orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)
            else:
                fighter_component = Fighter(hp=16, defense=1, power=4)
                ai_component = BasicMonster()
                monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True,fighter=fighter_component, ai=ai_component, death_function=monster_death)

            # Finally, append the valid monster to the objects list.
            objects.append(monster)

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


    # Show the player's stats.
    libtcod.console_set_default_foreground(con, libtcod.white)
    libtcod.console_print_ex(con, 1, SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.LEFT, 'HP: '+str(player.fighter.hp)+'/'+str(player.fighter.max_hp))

    # Blit the contents of "con" to the root console and present it.
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)                                               # Blit from the buffer console to the base console from the origin pixel to the max screen size.

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

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: INPUT HANDLING
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def handle_keys():
    global fov_recompute

    key = libtcod.console_wait_for_keypress(True)                                                                       # Stops all code execution until a key is pressed, unlike check_for_keypress.

    # Hot keys
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'                                                                                                   # Exits game.

    # Movement Keys. If we are playing and have have moved, FOV must be recomputed.
    if game_state == 'playing':
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            player_move_or_attack(0, -1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            player_move_or_attack(0, 1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            player_move_or_attack(-1, 0)
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            player_move_or_attack(1, 0)
        else:
            return 'didnt-take-turn'

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: MONSTER DEATH HANDLING
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def player_death(player)
    global game_state
    print 'You died!'
    game_state = 'dead'
    player.char = '%'
    player.color = libtcod.dark_red

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: MONSTER DEATH HANDLING --- Transform it into a corpse and cleanup its components.
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def monster_death(monster)
    print monster.name.capitalize() + ' is dead!'
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()                                                                                              # Ensures that all other objects draw on top of this monster's corpse.

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# INITIALIZE AND MAIN LOOP
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Init console(s)
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "python/Baby's first RL", False)                                # Initialize the default (base) console. This is where we will blit all graphics to.
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)                                                                  # Initialize another console to act as a buffer.

# Create Player object and put it into the objects list.
fighter_component = Fighter(hp=30, defense=2, power=5)
player = Object(0, 0, '@', 'player', libtcod.white, blocks = True, fighter=fighter_component, death_function=player_death)
player.x = 25
player.y = 23
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

#################################
# MAIN LOOP
#################################
while not libtcod.console_is_window_closed():
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