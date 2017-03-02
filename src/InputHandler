import libtcod

class InputHandler():
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # FUNCTION DEF: KEY HANDLING
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    def handle_keys(self):
        global key

        if key.vk == libtcod.KEY_ENTER and key.lalt:
            # Alt+Enter: toggle fullscreen
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        elif key.vk == libtcod.KEY_ESCAPE:
            return 'exit'  # exit game

        if game_state == 'playing':
            # Movement keys
            if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
                player_move_or_attack(0, -1)
            elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
                player_move_or_attack(0, 1)
            elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
                player_move_or_attack(-1, 0)
            elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
                player_move_or_attack(1, 0)
            elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
                player_move_or_attack(-1, -1)
            elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
                player_move_or_attack(1, -1)
            elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
                player_move_or_attack(-1, 1)
            elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
                player_move_or_attack(1, 1)
            elif key.vk == libtcod.KEY_KP5:
                pass  # Do nothing ie wait for the monster to come to you

            else:
                # Test for other keys
                key_char = chr(key.c)

                if key_char == 'c':
                    # Show character information
                    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                    msgbox(
                        'Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(
                            player.fighter.xp) +
                        '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(
                            player.fighter.max_hp) +
                        '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' + str(player.fighter.defense),
                        CHARACTER_SCREEN_WIDTH)

                if key_char == 'g':
                    # Pick up an item
                    for object in objects:  # look for an item in the player's tile
                        if object.x == player.x and object.y == player.y and object.item:
                            object.item.pick_up()
                            break

                if key_char == 'i':
                    # Show the inventory; if an item is selected, use it
                    chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                    if chosen_item is not None:
                        chosen_item.use()

                if key_char == 'd':
                    # Show the inventory; if an item is selected, drop it
                    chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                    if chosen_item is not None:
                        chosen_item.drop()

                if key_char == '<':
                    # Go down stairs, if the player is on them
                    if stairs.x == player.x and stairs.y == player.y:
                        next_level()

                return 'didnt-take-turn'