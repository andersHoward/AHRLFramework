from lib import libtcodpy as libtcod

from src import Constants as CONST


class Renderer(mainConsole, player):
    def __init__(self):
        pass

    def render_all(self):
        '''Main render update call for game loop.'''
        global fov_map, color_dark_wall, color_light_wall
        global color_dark_ground, color_light_ground
        global fov_recompute

        # Recompute FOV if necessary, then draw tiles based on their current visibility to the player.
        if fov_recompute:
            fov_recompute = False
            libtcod.map_compute_fov(fov_map, player.x, player.y, CONST.TORCH_RADIUS, CONST.FOV_LIGHT_WALLS, CONST.FOV_ALGO)
            for y in range(CONST.MAP_HEIGHT):                                                                                     # Draw all tiles in the map.
                for x in range(CONST.MAP_WIDTH):
                    visible = libtcod.map_is_in_fov(fov_map, x, y)                                                          # Check visibility of this tile.
                    wall = map[x][y].block_sight
                    if not visible:                                                                                         # Tile out of player FOV.
                        # If it's not visible right now, the player can only see it if it's explored
                        if map[x][y].explored:
                            if wall:
                                libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                            else:
                                libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                    else:                                                                                                   # Tile IN player FOV.
                        if wall:
                            libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET)

                            # Since it's visible, explore it.
                            map[x][y].explored = True

        # Draw all objects in the object list, but draw the player last on top of everything.
        for object in objects:
            if object != player:
                object.draw()
        player.draw()

        # Blit the contents of "con" to the root console.
        libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)                                               # Blit from the buffer console to the base console from the origin pixel to the max screen size.

        # Prepare to render the GUI panel
        libtcod.console_set_default_background(panel, libtcod.black)
        libtcod.console_clear(panel)

        # Print the game messages, one line at a time
        y = 1
        for (line, color) in game_msgs:
            libtcod.console_set_default_foreground(panel, color)
            libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
            y += 1

        # Show the player's stats.
        render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)

        # Print current dungeon level/location.
        libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))

        # display names of objects under the mouse
        libtcod.console_set_default_foreground(panel, libtcod.light_gray)
        libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

        # blit the contents of "panel" to the root console
        libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

    # If object is in FOV OR as been explored and is set to "always visible", set the color and then draw the character
    # that represents this item at its current position.
    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y) or (self.always_visible and map[self.x][self.y].explored):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    # Moves this object to the back of the objects list. Useful for affecting draw order.
    def send_to_back(self):
        global objects
        objects.remove(self)
        objects.insert(0, self)

    # Erase the character that represents this object.
    def clear(self):
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
