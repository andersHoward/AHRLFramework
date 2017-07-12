"""Global constants."""

from enum import Enum

from lib import libtcodpy as libtcod


# Actual size of the window.
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 100
LIMIT_FPS = 20

# GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_PIXEL_WIDTH = 50

# YAML CONFIG PATHS
YAML_MANIFEST_PATH = "config/config_manifest.yaml"

# INVENTORY
INVENTORYSLOTS_ROWS = 6
INVENTORYSLOTS_COLUMNS = 4

# MAP GENERATION ENUMS
# Terrain Flags
class ETerrainFlags(Enum):
    NONE = 0
    FLOOR_STONE = 1
    FLOOR_DIRT = 1.1
    FLOOR_GRASS = 1.2
    FLOOR_DRY_GRASS = 1.3
    SHALLOW_WATER = 3
    DEEP_WATER = 4
    WALL = 5
    CHASM = 5.1

# Map attributes
MAP_WIDTH = 160
MAP_HEIGHT = 90
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
FOV_ALGO = 1
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
LEVEL_SCREEN_WIDTH = 80
CHARACTER_SCREEN_WIDTH = 60

# TERRAIN COSTS
TERRAIN_COSTS = {
    'FLOOR': 0,
    'HILL': 2,
    'FOLIAGE': 2,
    'DENSE FOLIAGE': 3,
    'SHALLOW WATER': 1,
    'DEEP WATER': 3


}

# Spell constants


# Experience and leveling


# Color Defs
COLOR_DARK_WALL = libtcod.Color(0, 0, 100)
COLOR_LIGHT_WALL = libtcod.Color(130, 110, 50)
COLOR_DARK_GROUND = libtcod.Color(50, 50, 150)
COLOR_LIGHT_GROUND = libtcod.Color(200, 180, 50)

# Etc.
DEBUG_MODE = False
LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"



# Spell Enums
class ESpellName(Enum):
    HEAL = 1
    BLINK = 2
    TELEPORT = 3
    CONFUSE = 4
    FIREBALL = 5
    PUSH = 6
    INVISIBILITY = 7
    LEVITATION = 8


class EElementTypes(Enum):
    FIRE = 1
    LIGHTNING = 2
    AIR = 3
    ICE = 4
    WATER = 5
    DIVINE = 6
    QI = 7
    CYBER = 8
    POISON = 9
    HOLY = 10
    UNHOLY = 11


class ESpellClass(Enum):
    DAMAGE = 1
    HEAL = 2


class EPersistentEffects(Enum):
    POISONED = 1
    BLEED = 2
    CRIPPLED = 3
    HUNGRY = 4
    VULNERABLE = 5
    WATER_SIGHT = 6
    SWIMMING = 7


class EAbilityTargetStyle(Enum):
    USER_SELECTED_NPC = 1
    USER_SELECTED_LOCATION = 2
    ORIGIN_BURST = 3


# Terrain and prop type enums.
class ETerrainTypes(Enum):
    FLAT_FLOOR = 1
    SHALLOW_WATER = 2
    DEEP_WATER = 3
    STRONG_CURRENT = 4
    SWAMP = 5
    GRASS = 6
    TALL_GRASS = 7
    TREE = 8
    BUSH = 9


class ETerrainAndPropAttributes(Enum):
    BLOCKING = 1
    NON_BLOCKING = 2
    BREAKABLE = 3
    TERMINAL = 4
    DOOR_N = 5
    DOOR_S = 6
    DOOR_E = 7
    DOOR_W = 8
