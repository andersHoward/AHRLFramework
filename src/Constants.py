"""Global constants."""

from lib import libtcodpy as libtcod
from enum import Enum

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
INVENTORY_PIXEL_WIDTH = 50

# Inventory
INVENTORYSLOTS_ROWS = 6
INVENTORYSLOTS_COLUMNS = 4

# Map attributes

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

# Spell Enums
E_SPELL_NAME = Enum('heal', 'blink', 'teleport', 'confusion', 'fireball', 'push', 'invisibility', 'levitation')
E_SPELL_TARGET_STYLE = Enum('user_selected_npc', 'user_selected_location', 'entity_origin_burst')
E_SPELL_ELEMENT = Enum('fire', 'lightning', 'air', 'ice', 'water', 'divine', 'qi', 'cyber', 'poison', 'holy', 'unholy')
E_SPELL_CLASS = Enum('heal', 'damage')
E_PERSISTENT_EFFECTS = Enum('poison', 'bleed', 'crippled', 'hungry', 'vulnerable')

# Spell constants
HEAL_AMOUNT_BASE = 40
LIGHTNING_DAMAGE = 30
LIGHTNING_RANGE = 5
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25

# Experience and leveling
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

# Color Defs
COLOR_DARK_WALL = libtcod.Color(0, 0, 100)
COLOR_LIGHT_WALL = libtcod.Color(130, 110, 50)
COLOR_DARK_GROUND = libtcod.Color(50, 50, 150)
COLOR_LIGHT_GROUND = libtcod.Color(200, 180, 50)

# Etc.
DEUB_MODE = False
LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

