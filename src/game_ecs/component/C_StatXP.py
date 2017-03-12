"""Gives the entity an XP pool."""

import Constants as CONST
import gui.GUI

class C_StatXP():
    def __init__(self, level_thresholds_yaml=None):
        self._level = 1
        _xp = 0

    @property
    def current_level(self):
        return self._level
