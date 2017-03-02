import libtcodpy

class E_NPC():
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # FUNCTION DEF: NPC DEATH HANDLING
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    def player_death(player):
        global game_state
        message('You died!', libtcod.red)
        game_state = 'dead'
        player.char = '%'
        player.color = libtcod.dark_red

    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # FUNCTION DEF: NPC DEATH HANDLING --- Transform it into a corpse and cleanup its components.
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    def monster_death(monster):
        message('The ' + monster.name + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points.',
                libtcod.orange)
        monster.char = '%'
        monster.color = libtcod.dark_red
        monster.blocks = False
        monster.fighter = None
        monster.ai = None
        monster.name = 'remains of ' + monster.name
        monster.send_to_back()