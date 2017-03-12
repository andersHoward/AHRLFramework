"""Init class sticks around to init and re-init the game."""

from lib import libtcodpy as libtcod
import Constants as CONST
from gui import GUI
import ecs.ecs as lib_ecs
from game_ecs import system as game_systems


class Init():

    def __init__(self):
        self.init_libtcod()
        managers = {'system_manager': lib_ecs.SystemManager, 'entity_manager': lib_ecs.EntityManager}
        systems = {'system_xp' : game_systems.}

        # Start the game. Main menu holds the main loop.
        GUI.GUI.main_menu()


    def init_libtcod(self):
        libtcod.console_set_custom_font('arial10x10.png',
                                        libtcod.FONT_TYPE_GREYSCALE |
                                        libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(CONST.SCREEN_WIDTH,
                                  CONST.SCREEN_HEIGHT,
                                  "RL Framework",
                                  False)  # Initialize the default (base) console. This is where we will blit all graphics to.
        libtcod.sys_set_fps(CONST.LIMIT_FPS)
        con = libtcod.console_new(CONST.SCREEN_WIDTH, CONST.SCREEN_HEIGHT)  # Initialize another console to act as a buffer.
        panel = libtcod.console_new(CONST.SCREEN_WIDTH, CONST.PANEL_HEIGHT)

    def new_game():
        '''Initialize all of the variables required for a new game.'''
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

        def next_level():
            '''Advances to next floor of the dungeon.'''
            global dungeon_level
            # Heal the player by 50%
            message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
            player.fighter.heal(player.fighter.max_hp / 2)

            message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
            dungeon_level += 1
            make_map()  # Create a fresh new level!
            initialize_fov()
