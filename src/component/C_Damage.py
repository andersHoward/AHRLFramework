"""Damage component."""


import Component
from ..rendering.GUI import GUI
from random import randint

class C_Damage(Component.Component):
    """Component class that handles damage output.

        TODO:
            Re-implement power property. Needs to calculate bonuses within ECS model.
            Re-implement attack.
    """

    defaults = dict([('normal_pct', 1.0), ('critical_pct', 1.5), ('base_damage', 10)])

    def __call__(self):
        '''Returns a damage calculation based on properties of the component.

            Testdoc:
        >>> from entity.Entity import Entity
        >>> player = Entity('player', 0)
        >>> player.damage = C_Damage(owner_entity=player, normal_pct=1.5, critical_pct = 2)
        '''
        crit = randint(0, 99) <= (self.critical_pct -1)
        damage_mult = self.normal_pct
        if crit:
            damage_mult = self.critical
        return damage_mult

    def __init__(self, normal_power_pct, critical_power_pct):
        """Damage component init."""
        self.base_power = normal_power_pct

    @property
    def attack_power(self):

        bonus = 1
        #TODO: bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
       # bonus = sum(owner_entity.equipment.attack_power_bonus for equipment in owner_entity.equipment.get_all_equipped() )
        return self.base_power + bonus

    # Make a target take damage.
    def attack(self, target_entity):
        damage = self.power - target_entity.defense

        if damage > 0:
            GUI.message(self.owner_entity.name.capitalize() + ' attacks ' + target_entity.name + ' for ' + str(damage) + ' hit points.')
            target_entity.health.take_damage(damage)
        else:
            GUI.message(self.owner_entity.name.capitalize() + ' attacks ' + target_entity.name + ' but it has no effect!')


if __name__ == '__main__':
    from doctest import testmod

    testmod()
