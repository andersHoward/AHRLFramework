import libtcodpy as libtcod


class MainJunction():
    '''Checks game state and transitions states.'''
    def __init__(self, state):
        self.state = state
        pass

    def check_game_state(self):
    '''TODO Returns the current game state'''

    def game_loop(self):
    '''TODO Checks for game termination conditions, else loops.'''
    global key, mouse, L_entities
    player_action = None
    mouse = libtcod.Mouse()
    key = libtcod.Key()
    player = Entity()
    #TODO Give player components

    while not libtcod.console_is_window_closed():
        # Render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        Renderer.render_all()
        libtcod.console_flush()                                                                                         # At the end of the main loop, you must present all changes to the screen. This is called Flushing.

        # Check for level up before anything else because if level up, we have to render the level up menu before all else.
        check_level_up()

        # Erase all objects at their old locations before they move.
        for entity in L_entities:
            entity.clear() #TODO Clear method should be part of entity render component.

        # Handle keys and exit game if needed
        player_action = handle_keys()                                                                                   # Break main game loop once we have an acceptable input.
        if player_action == 'exit':
            save_game()                                                                                                 # Save game state when exiting.
            break

        # After player takes turn, NPCs take turn.
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for entity in objects:
                if entity.ai:
                    entity.ai.take_turn()