import Constants as CONST

def create_room(room):
    '''Take a Rectangle and make all of its tiles passable.'''
    global map

    # Iterate through tiles in a placed room (i.e. a Rect()), and make them passable.
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    '''Takes two columns on a row and makes the tiles between them passable.'''
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    '''Takes two rows on a column and makes the tiles between them passable.'''
    global map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def make_map():
    '''Main function that creates the dungeon. TODO clean this up/break it up.'''

    # Nested List Comprehension to fill the map with "unblocked" tiles.
    global map, player, L_entities, stairs
    L_entities = [player]

    # First, fill map with blocked tiles.
    map = [[Tile(True)
            for y in range(CONST.MAP_HEIGHT)]
           for x in range(CONST.MAP_WIDTH)]

    # Generate a random number of randomly sized rooms out of our solid world.
    rooms = []
    num_rooms = 0

    # Randomize the params of a room.
    for r in range(CONST.MAX_ROOMS):
        w = libtcod.random_get_int(0, CONST.ROOM_MIN_SIZE, CONST.ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, CONST.ROOM_MIN_SIZE, CONST.ROOM_MAX_SIZE)
        x = libtcod.random_get_int(0, 0, CONST.MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, CONST.MAP_HEIGHT - h - 1)

        # Create a Rect with the randomized attributes.
        new_room = Rect(x, y, w, h)

        # Check our new room against all existing rooms for overlap.
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        # Room is valid; carve it out of the solid world.
        if not failed:
            create_room(new_room)
            (new_x, new_y) = new_room.center()

            # DEBUG MODE: print "room number" to see how the map drawing worked
            if CONST.DEBUG_MODE == True:
                room_no = Object(new_x, new_y, chr(65 + num_rooms), 'room number', libtcod.white)
                L_entities.insert(0, room_no)  # draw early, so monsters are drawn on top

            # Start player in first room.
            if num_rooms == 0:
                player.x = new_x
                player.y = new_y
            else:                                                                                                               # All rooms after the first must be connected via a tunnel that we create here.
                # Get the centerpoint of the previous room. We'll use that as our connection target.
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                # Flip a coin to determine the connecting hall's directionality.
                if libtcod.random_get_int(0, 0, 1) == 1:
                    # first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    # first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

        # Add some contents to this room, such as monsters
        place_objects(new_room)

        # Finally, append the new room to the list
        rooms.append(new_room)
        num_rooms += 1

    # Create stairs at the center of the last room
    stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white, True)
    L_entities.append(stairs)
    stairs.send_to_back()  # so it's drawn below the monsters

def place_objects(room):
    '''Takes a room and places randomized objects in it. TODO Clean this up.'''
    # CREATE TABLES FOR OBJECT ROLL CHANCES, AND THEIR CHANCE ADVANCEMENTS TO PASS TO from_dungeon_level().
    # Maximum number of monsters per room
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])

    # Chance of each monster
    monster_chances = {}
    monster_chances['orc'] = 80  # orc always shows up, even if all other monsters have 0 chance
    monster_chances['troll'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])

    # Maximum number of items per room
    max_items = from_dungeon_level([[1, 1], [2, 4]])

    # Chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}
    item_chances['heal'] = 35  # healing potion always shows up, even if all other items have 0 chance
    item_chances['lightning'] = from_dungeon_level([[25, 4]])
    item_chances['fireball'] = from_dungeon_level([[25, 6]])
    item_chances['confuse'] = from_dungeon_level([[10, 2]])
    item_chances['sword'] = from_dungeon_level([[5, 4]])
    item_chances['shield'] = from_dungeon_level([[15, 8]])

    # Choose random number of monsters.
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)

    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1, room.x2)
        y = libtcod.random_get_int(0, room.y1, room.y2)

        # If the random location is not blocked, go ahead and create the monster object.
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)
            if choice == 'orc':  # 80% chance of getting an orc, else troll.
                fighter_component = Fighter(hp=20, defense=0, power=4, xp=35, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True,
                                 fighter=fighter_component, ai=ai_component)
            elif choice == 'troll':
                fighter_component = Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True, fighter=fighter_component,
                                 ai=ai_component)

            # Finally, append the valid monster to the objects list.
            objects.append(monster)

    # Choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_items)

    # Distribute random items in random (unblocked) locations.
    for i in range(num_items):
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'heal':
                # Create a healing potion
                item_component = Item(use_function=cast_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)
            elif choice == 'lightning':
                # Create lightning bolt scroll.
                item_component = Item(use_function=cast_lightning)
            elif choice == 'fireball':
                # Create a fireball scroll.
                item_component = Item(use_function=cast_fireball)
                item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)
            elif choice == 'confuse':
                # Create a confuse scroll
                item_component = Item(use_function=cast_confuse)
                item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)
            elif choice == 'sword':
                # create a sword
                equipment_component = Equipment(slot='right hand', power_bonus=3)
                item = Object(x, y, '/', 'sword', libtcod.sky, equipment=equipment_component)
            elif choice == 'shield':
                # create a shield
                equipment_component = Equipment(slot='left hand', defense_bonus=1)
                item = Object(x, y, '[', 'shield', libtcod.darker_orange, equipment=equipment_component)

            objects.append(item)
            item.send_to_back()  # Items appear below other objects
            item.always_visible = True

        def initialize_fov():
            '''Initialize the FOV map. TODO This might be a dungeon generator function.'''
            global fov_recompute, fov_map
            fov_recompute = True

            # Create the FOV map: create a duplicate (but inverse) FOV map according to the generated game map.
            fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
            for y in range(MAP_HEIGHT):
                for x in range(MAP_WIDTH):
                    libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

            # Unexplored areas start black (which is the default background color)
            libtcod.console_clear(con)