import libtcodpy as libtcod
import math
import textwrap
import shelve

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTION DEF: PLAY GAME --- The main game loop.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def play_game():
    global key, mouse
    player_action = None
    mouse = libtcod.Mouse()
    key = libtcod.Key()

    while not libtcod.console_is_window_closed():
        # Render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()
        libtcod.console_flush()                                                                                         # At the end of the main loop, you must present all changes to the screen. This is called Flushing.

        # Check for level up before anything else because if level up, we have to render the level up menu before all else.
        check_level_up()

        # Erase all objects at their old locations before they move.
        for object in objects:
            object.clear()

        # Handle keys and exit game if needed
        player_action = handle_keys()                                                                                   # Break main game loop once we have an acceptable input.
        if player_action == 'exit':
            save_game()                                                                                                 # Save game state when exiting.
            break

        # After player takes turn, NPCs take turn.
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

# System Init: Initialize console(s)
Init.InitConsoles()                                                                                                           # Load the Main Menu to begin the game!