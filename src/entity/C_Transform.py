class C_Transform(Component):
    '''Component that gives an Entity a position in the world.
        Args:
            x (int): initial x position in cellular matrix
            y (int): initial y position in cellular matrix
            z (int): initial z position in cellular matrix'''

    def __init__(self, x=None, y=None, z=None):
        global position
        position = (x,y,z)

    def get_position(self):
        return position

    def set_position(self, x, y, z):
        Position = (x, y, z)