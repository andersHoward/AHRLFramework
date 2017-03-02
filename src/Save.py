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