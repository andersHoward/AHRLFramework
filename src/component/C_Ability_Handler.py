class C_Ability_Handler():
    ''' Component that allows an entity to spawn effects into the world.'''

    def cast_heal():
        '''Heal the target entity.'''
        if player.fighter.hp == player.fighter.max_hp:
            message('You are already at full health.', libtcod.red)
            return 'cancelled'

        message('Your wounds start to feel better!', libtcod.light_violet)
        player.fighter.heal(HEAL_AMOUNT)

    def cast_lightning():
        '''Find the nearest enemy within max range and damage it.'''
        monster = closest_monster(LIGHTNING_RANGE)
        if monster is None:
            message('No enemy is close enough to strike.', libtcod.red)
            return 'cancelled'

        # Zap it!
        message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
                + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.blue)
        monster.fighter.take_damage(LIGHTNING_DAMAGE)

    def cast_confuse():
        '''Apply the Confuse effect to an enemy.'''
        message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
        monster = target_monster(CONFUSE_RANGE)
        if monster is None: return 'cancelled'

        # Else replace the nearest monster's AI with a "confused" one; after some turns it will restore the old AI
        old_ai = monster.ai
        monster.ai = ConfusedMonster(old_ai)
        monster.ai.owner = monster  # tell the new component who owns it
        message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!',
                libtcod.light_green)

    def cast_fireball():
        '''Spawn a fireball projectile towards a chosen enemy.'''
        message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
        (x, y) = target_tile()
        if x is None: return 'cancelled'
        message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)

        for obj in objects:  # damage every fighter in range, including the player
            if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
                message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
                obj.fighter.take_damage(FIREBALL_DAMAGE)
