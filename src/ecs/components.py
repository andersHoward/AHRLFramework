#   ___                                  _      
#  / __|___ _ __  _ __  ___ _ _  ___ _ _| |_ ___
# | (__/ _ \ '  \| '_ \/ _ \ ' \/ -_) ' \  _(_-<
#  \___\___/_|_|_| .__/\___/_||_\___|_||_\__/__/
#                |_| 
# Class definitions for each individual component type derived from Component.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

from Component import Component

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# COMPONENT CLASS DEF: FIGHTER --- Component that adds combat properties and methods to a base object instance.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Fighter:
    def __init__(self, hp, defense, power, xp, death_function=None):
        defaults = dict((hp=10), (defense = 10), )
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

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# COMPONENT CLASS DEF: BASICMONSTER --- Component that adds basic AI routines to an object instance.
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class BasicMonster:
    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):                                                         # Monster sees you if you see it. TODO something better?

            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)

            # Close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# COMPONENT CLASS DEF: CONFUSEDMONSTER --- AI for a temporarily confused monster (reverts to previous AI after a while).
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class ConfusedMonster:
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

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
