"""Damage component."""


import Component
from random import randint

class C_Damage(Component):
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

    def __init__(self, power, death_function=None):
        """Damage component init."""

        self.base_power = power

    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_power + bonus

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

if __name__ == '__main__':
    from doctest import testmod

    testmod()
