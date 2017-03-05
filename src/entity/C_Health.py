import Component

class C_Health(Component):
    ''' Component class that manages Entity hitpoints.'''

    def __init__(self, max_hp):
        super(C_Health, self).__init__(owner, **properties)
        defaults = dict(('current', 100), ('max', 100))

    @property
    def alive(self):
        return self.current > 0