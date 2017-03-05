"""Module that contains the Inventory Component class."""


class C_Inventory():
    """Component that adds an inventory of items to an entity.

        Todo:
            Write this dang class.
    """

    def __init__():
        """Inventory Component initialization."""
        pass

    def get_equipped_in_slot(inventory, slot):
        """ Returns the equipment that is in the queried slot.

                Args:
                    inventory (Inventory): the inventory component of the
                    queried entity.
        """
        inventory = inventory
        slot = slot

        for obj in inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None
