"""Module that contains the Inventory Component class."""


class C_Inventory():
    """Component that adds an inventory of items to an entity.

        Todo:
            Write this dang class.
    """

    @property
    def inventory(self):
        """Inventory getter."""
        pass

    @inventory.setter
    def inventory(self, value):
        """Inventory setter."""
        self.inventory = value

    @property
    def equipped_inventory(self):
        """Equipped inventory getter."""
        pass

    @equipped_inventory.setter
    def inventory(self, value):
        """Equipped inventory setter."""
        pass

    def __init__(self):
        """Inventory Component initialization."""
        pass

    def get_equipped_in_slot(self, inventory, slot):
        """Returns the equipment that is in the queried slot.

                Args:
                    inventory (Inventory): the inventory component of the
                    queried entity."""
        inventory = inventory
        slot = slot

        for obj in inventory:
            if obj.equipment and obj.equipment.slot == slot and \
               obj.equipment.is_equipped:
                return obj.equipment
        return None
