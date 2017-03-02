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