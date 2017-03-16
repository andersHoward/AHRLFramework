"""Init class sticks around to init and re-init the game."""

from gui import GUI
import logging
import Constants as CONST
import ecs.ecs as lib_ecs
from game_ecs import system as game_systems
from lib import libtcodpy as libtcod
import MapGenerator

class Init():
    """Init class sticks around to init new games/levels."""

    def __init__(self, log):
        """Init() __init__."""
        self.init_libtcod()
        managers = {'system_manager': lib_ecs.SystemManager,
                    'entity_manager': lib_ecs.EntityManager
                    }
        systems = {'system_xp': game_systems}
        logging.info("Init.__init__(): ECS systems initialized.")

        # Start the game. Main menu holds the main loop.
        GUI.GUI.main_menu()

     def init_libtcod(self):
        """Opens the default console, plus two buffer consoles."""
        # Initialize the base console. This is where we will 
        # blit all consoles down to.
        libtcod.console_set_custom_font('arial10x10.png',
                                        libtcod.FONT_TYPE_GREYSCALE |
                                        libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(CONST.SCREEN_WIDTH,
                                  CONST.SCREEN_HEIGHT,
                                  "RL Framework",
                                  False)
        libtcod.sys_set_fps(CONST.LIMIT_FPS)
        con = libtcod.console_new(CONST.SCREEN_WIDTH, CONST.SCREEN_HEIGHT)  # Initialize another console to act as a buffer.
        panel = libtcod.console_new(CONST.SCREEN_WIDTH, CONST.PANEL_HEIGHT)
        logging.info("Init.init_libtcod(): libtcod consoles initialized.")

    def new_game():
        '''Initialize all of the variables required for a new game.'''
        pass

    def next_level():
        '''TODO: Advances to next floor of the dungeon.'''
        MapGenerator.make_map()  # Create a fresh new level!
        MapGenerator.initialize_fov()
