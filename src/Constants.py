#  _____ _____ _   _  _____ _____ ___   _   _ _____ _____
# /  __ \  _  | \ | |/  ___|_   _/ _ \ | \ | |_   _/  ___|
# | /  \/ | | |  \| |\ `--.  | |/ /_\ \|  \| | | | \ `--.
# | |   | | | | . ` | `--. \ | ||  _  || . ` | | |  `--. \
# | \__/\ \_/ / |\  |/\__/ / | || | | || |\  | | | /\__/ /
#  \____/\___/\_| \_/\____/  \_/\_| |_/\_| \_/ \_/ \____/
#
'''Global constants.'''
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