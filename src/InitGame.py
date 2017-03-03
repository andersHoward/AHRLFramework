import libtcodpy as libtcod
import Constants as CONST
import GUI

class Init():
    def InitConsoles(self):
        libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(CONST.SCREEN_WIDTH, CONST.SCREEN_HEIGHT, "python/AH RL Framework",
                                  False)  # Initialize the default (base) console. This is where we will blit all graphics to.
        libtcod.sys_set_fps(CONST.LIMIT_FPS)
        con = libtcod.console_new(CONST.SCREEN_WIDTH, CONST.SCREEN_HEIGHT)  # Initialize another console to act as a buffer.
        panel = libtcod.console_new(CONST.SCREEN_WIDTH, CONST.PANEL_HEIGHT)

        GUI.main_menu()

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