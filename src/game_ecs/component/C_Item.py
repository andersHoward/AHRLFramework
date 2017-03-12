"""Module that contains the Item Component class."""


class C_Item():
    """Component that allows an object to be picked up and used."""

    def __init__(self, owner, use_function=None):
        '''CItem Init:

        Args:
            use_function (str): the name of the function that should execute
            when this item is used.
        '''
        global use_function
        global owner
        global inventory

        self.use_function = use_function
        self.owner = owner
        inventory = owner.inventory


    def pick_up(self):
        '''Add item to the player's inventory and remove it from map.'''

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