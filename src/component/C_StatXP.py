"""Gives the entity an XP pool."""

import Constants as CONST
import gui.GUI

class C_StatXP():

    def __init__(self, level_thresholds, player):
        player = player
        level_thresholds = level_thresholds

    def check_level_up():
        level_up_xp = CONST.LEVEL_UP_BASE + player.level * CONST.LEVEL_UP_FACTOR
        if player.fighter.xp >= level_up_xp:
            player.level += 1
            player.fighter.xp -= level_up_xp
            GUI.message('Your skills grow stronger. You reached level ' + str(player.level) + '!', libtcod.yellow)

            # Ask for a skill advancement choice until one is made.
            choice = None
            while choice == None:
                choice = menu('Level up! Choose a stat to raise:\n',
                              ['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
                               'Strength (+1 attack, from ' + str(player.fighter.power) + ')',
                               'Agility (+1 defense, from ' + str(player.fighter.defense) + ')'], LEVEL_SCREEN_WIDTH)

            if choice == 0:
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif choice == 1:
                player.fighter.base_power += 1
            elif choice == 2:
                player.fighter.base_defense += 1
