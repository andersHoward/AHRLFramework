from collections import OrderedDict as dict


class C_Health(component.Component):
    ''' Component class that manages Entity hitpoints.

    Testdoc:
    >>> from entity.Entity import Entity
    >>> player = Entity('player', 0)
    >>> player.health = C_Health(player, current_health=80, death_function=None)
    >>> player.health
    <Health entity:player.health>
    >>> print player.health
    {
        "current_health": 80,
        "max_health": 100
    }
    >>> print player.health.current_health
    80
    >>> print player.health['current_health']
    80
    >>> player.health['current_health'] = 65
    >>> print player.health
    {
        "current_health": 65
        "max_health": 100
    }
    '''

    def __init__(self, current_health):
        super(C_Health, self).__init__()
        defaults = dict([('current_health', 100), ('max_health', 100), ('death_function', None)])

    @property
    def alive(self):
        return self.current_health > 0

    def take_damage(self, amount):
        pass

    def kill(self):
        pass

    def death_function(self):
        pass

if __name__ == '__main__':
    from doctest import testmod

    testmod()
