#   ___                                  _      
#  / __|___ _ __  _ __  ___ _ _  ___ _ _| |_ ___
# | (__/ _ \ '  \| '_ \/ _ \ ' \/ -_) ' \  _(_-<
#  \___\___/_|_|_| .__/\___/_||_\___|_||_\__/__/
#                |_|
'''Module that contains definitions for each individual component type derived
from Component.'''
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import libtcodpy as libtcod
from Component import Component


class C_Damage(Component):
    '''Component class that handles basic damage output.'''

    def __init__(self, hp, defense, power, xp, death_function=None):
        defaults = dict((hp=10), (defense = 10))
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.death_function = death_function

    # PROPERTIES
    # E.g. When player.power is accessed, this function is called instead of accessing the property directly.
    #   This allows us to sum the bonuses from all equipped items and buffs at run time, rather than having items and
    #   buffs modifying the player stat directly which can easily cause bugs.

    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_power + bonus

    @property
    def defense(self):  # return actual defense, by summing up the bonuses from all equipped items
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
        return self.base_defense + bonus

    @property
    def max_hp(self):  # return actual max_hp, by summing up the bonuses from all equipped items
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus

    # Make a target take damage.
    def attack(self, target):
        damage = self.power - target.fighter.defense

        if damage > 0:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage

        # Check for death and call death function.
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)

        # Award XP.
        if self.owner != player:
            player.fighter.xp += self.xp

    def heal(self, amount):

        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

class C_Transform(Component):
    '''Component that gives an Entity a position in the world.
        Args:
            x (int): initial x position in cellular matrix
            y (int): initial y position in cellular matrix
            z (int): initial z position in cellular matrix'''

    def __init__(self, x=None, y=None, z=None):
        global Position = (x,y,z)

    def get_position(self):
        return Position

    def set_position(self, x, y, z):
        Position = (x, y, z)

class C_Mover(Component):
    '''Component that  allows an entity some mode of travel.
            Args:
                transport_mode (str): name of the mode of travel to append to the entity.'''

    def __init__(self, transport_mode):
        transport_mode = transport_mode

    def player_move_or_attack(dx, dy, player):
        global fov_recompute, L_entities

        # Coordinates the player is trying to act upon.
        x = player.x + dx
        y = player.y + dy

        # Try to find attackable entity at target tile.
        target = None
        for entity in L_entities:
            if entity.fighter and entity.x == x and entity.y == y:
                target = entity
                break

        # Attack if entity found, else move
        if target is not None:
            player.fighter.attack(target)
        else:
            player.move(dx, dy)
            fov_recompute = True

    # Move by the given amount.
    def Try_Move(self, dx, dy):
        if not is_blocked(self.x + dx,
                          self.y + dy):  # Check if the tile we're trying to move into is a blocking tile or contains a blocking object.
            self.x += dx
            self.y += dy

    # Moves object towards a target location. Normally used for simple AI.
    def move_towards(self, target_x, target_y):
        # Get vector.
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normalize to a unit vector (of 1), then round to int so movement is restricted to the grid, then move.
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

class C_Health(Component):
    ''' TODO Component class that manages Entity Hitpoints.'''
    def __init__(self, max_hp):
        Component.__init__(self) # Call superclass init.

    defaults = dict(('current', 100), ('max', 100))

    @property
    def alive(self):
        return self.current > 0


class C_AI_State_Machine():
    ''' TODO Allows an Entity to posses an AI state machine that manages 
    AI state classes.'''

    # Move randomly if still confused, else revert back to normal AI.
    def take_turn(self):
        if self.num_turns > 0:  # still confused...
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1

        else:
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# COMPONENT CLASS DEF: ITEM --- Component that allows an object to be picked up and used.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Item:
    def __init__(self, use_function=None):
        self.use_function = use_function

    # Add to the player's inventory and remove from the map
    def pick_up(self):

        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)

            # Special case: automatically equip, if the corresponding equipment slot is unused and the picked-up item
            #               is equippable.
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()

    # Equip an item or call its use function.
    def use(self):
        # If the object has an Equipment component, it can be equipped.
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        # Else just call the use function if it is defined.
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  # destroy after use, unless it was cancelled for some reason

    # Add to the map and remove from the player's inventory. also, place it at the player's coordinates
    def drop(self):
        # Special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()

        # add to the map and remove from the player's inventory. also, place it at the player's coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# COMPONENT CLASS DEF: EQUIPMENT --- Component that allows an object to be equipped to yield bonuses.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Equipment:
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.slot = slot
        self.is_equipped = False

    # Toggle don/doff status.
    def toggle_equip(self):
        if self.is_equipped:
            self.doff()
        else:
            self.equip()

    # Equip object.
    def equip(self):
        # If the slot is already being used, doff whatever is there first
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.doff()

        self.is_equipped = True
        message('Equipped ' + self.owner.name + 'on ' + self.slot + '.', libtcod.light_green)

    # Doff object.
    def doff(self):
        if not self.is_equipped: return
        self.is_equipped = False
        message('Doffed ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)
