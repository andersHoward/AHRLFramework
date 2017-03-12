"""ECS system that works on C_StatXP Components."""
from game_ecs.ecs.models import System

class SYS_XP(System):

    def __init__(self):
        pass

    def check_level_up(self, entity):
        # Check if entity has exceeded a level threshold. If true, increment level.
        pass

    def gain_xp(self, amount):
        self._xp += amount
        self.check_level_up()
