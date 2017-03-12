from lib import libtcodpy as libtcod


class GUI():
    def __init__(self):
        pass

    def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
        '''Renders a generic bar (HP, experience, etc).

        Args:
            x: The pixel-width of the bar.
            y: The pixel-height of the bar.
            name: Name of the stat that the bar is measuring, to display on the bar.
            value: The current value of the stat that the bar is displaying.
            maximum: The max value of the stat that the bar is displaying.
            bar_color: The color that the filled portion of the bar will be.
            back_color: The color that the non-filled portion of the bar will be.
        '''
        bar_width = int(float(value) / maximum * total_width)

        # Render the background first
        libtcod.console_set_default_background(panel, back_color)
        libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

        # Now render the bar on top
        libtcod.console_set_default_background(panel, bar_color)
        if bar_width > 0:
            libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

        # Finally, some centered text with the values
        libtcod.console_set_default_foreground(panel, libtcod.white)
        libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                                 name + ': ' + str(value) + '/' + str(maximum))

    def message(new_msg, color=libtcod.white):
        ''' Formats a string and inserts it into the message log.'''
        # split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

        for line in new_msg_lines:
            # if the buffer is full, remove the first line to make room for the new one
            if len(game_msgs) == MSG_HEIGHT:
                del game_msgs[0]

            # add the new line as a tuple, with the text and the color
            game_msgs.append((line, color))

    def menu(header, options, width):
        if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

        # calculate total height for the header (after auto-wrap) and one line per option
        header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
        if header == '':
            header_height = 0
        height = len(options) + header_height

        # create an off-screen console that represents the menu's window
        window = libtcod.console_new(width, height)

        # print the header, with auto-wrap
        libtcod.console_set_default_foreground(window, libtcod.white)
        libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

        # print all the options
        y = header_height
        letter_index = ord('a')
        for option_text in options:
            text = '(' + chr(letter_index) + ') ' + option_text
            libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
            y += 1
            letter_index += 1

        # blit the contents of "window" to the root console
        x = SCREEN_WIDTH / 2 - width / 2
        y = SCREEN_HEIGHT / 2 - height / 2
        libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

        # present the root console to the player and wait for a key-press
        libtcod.console_flush()
        key = libtcod.console_wait_for_keypress(True)

        # Special Case: toggle fullscreen
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        # convert the ASCII code to an index; if it corresponds to an option, return it
        index = key.c - ord('a')
        if index >= 0 and index < len(options): return index
        return None

    def inventory_menu(header):
        if len(inventory) == 0:
            options = ['Inventory is empty.']
        else:
            options = []
            for item in inventory:
                text = item.name
                # Show additional information, in case it's equipped.
                if item.equipment and item.equipment.is_equipped:
                    text = text + ' (on ' + item.equipment.slot + ')'
                options.append(text)

        index = menu(header, options, INVENTORY_WIDTH)

        # if an item was chosen, return it
        if index is None or len(inventory) == 0: return None
        return inventory[index].item

    def msgbox(text, width=50):
        menu(text, [], width)

    def main_menu():
        img = libtcod.image_load('menu_background1.png')

        while not libtcod.console_is_window_closed():
            # Show the background image at twice the normal console resolution
            libtcod.image_blit_2x(img, 0, 0, 0)

            # show the game's title, and some credits!
            libtcod.console_set_default_foreground(0, libtcod.light_yellow)
            libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 4, libtcod.BKGND_NONE, libtcod.CENTER,
                                     'SOME FUCKING GAME')
            libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER,
                                     'By SOME FUCKING DUDES')

            # Show options and wait for the player's choice.
            choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
            if choice == 0:
                new_game()
                play_game()
            if choice == 1:
                try:
                    load_game()
                except:
                    msgbox('\n No saved game to load.\n', 24)
                    continue
                play_game()
            elif choice == 2:
                break
