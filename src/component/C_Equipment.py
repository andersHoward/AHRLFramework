class C_Equipment(C_Item):
    """Component that allows an item to be equipped to yield bonuses.

        Todo:
            This is currently hard-coded according to the Jotaf tutorial.
            Instead, make it take a Gameplay_Effect to determine the bonus.
    """

    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        """C_Equipment init."""
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
