"""AI States module for AI FSM."""
from .. import Constants as CONST
import libtcodpy as libtcod


class AIState():
    '''Base class for AI states.
        Args:

        Todo:'''

    def __init__(self, owner, player, previous_state="Dormant"):
        global state_name
        global E_ai_states
        global owner
        global player
        global previous_state
        previous_state = previous_state
        player = player
        owner = owner
        E_ai_states = ("Dormant", "Sleeping", "Hunting", "Following")
        state_name = None

    def take_turn(self):
        pass
    def __repr__(self):
        class_name = self.__class__.__name__
        return "<{}: {}>".format(class_name, self.state_name)
    def get_state_name(self):
        return state_name


class AIS_simple_move(AIState):
    ''' Monster sees you if you see it and will try to kill you.'''
    def __init__(self):
        super(AIS_simple_move, self).__init__(owner, player, previous_state)

    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(CONST.fov_map, monster.x, monster.y):

            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)

            # Close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)


class AIS_confused(AIState):
    def __init__(self, old_ai_state, num_turns=CONST.CONFUSE_NUM_TURNS):
        super(AIS_simple_move, self).__init__(owner, player, previous_state)
        self.num_turns = num_turns