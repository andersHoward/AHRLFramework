class GameState():
    ''' Holds the state of the game and functions to check it.
        Args:
            init_state (str) : State to initialize into.

        Todo:
            transition_state method implementation.
            The various states themselves (their loops).
            When Playstate first created, pass it starting game conditions.
    '''

    def __init__(self, init_state):
        '''GameState.__init__'''
        global current_state
        global main_menu
        global game_over
        global quit
        global play
        current_state = init_state
        main_menu = "main_menu"
        game_over = "game_over"
        quit = "quit"
        play = "play"

        global game_states
        game_states = (main_menu, game_over, quit, play)

    def __repr__(self):
        return "<GameState: {}>".format(self.current_state)

    def get_current_state(self):
        return current_state

    def transition_state(target_state)
        pass

class GS_Play_State(GameState):
    ''' GameState: Play_State. Initializes game conditions and runs the main
         loop for the game.'''

    def __init__(self):
        pass
