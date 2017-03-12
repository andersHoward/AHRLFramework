from ecs import ecs

class C_Mover():
    '''Component that  allows an entity some mode of travel.
            Args:
                transport_mode (str): name of the mode of travel to append to the entity.'''

    def __init__(self, transport_mode):
        transport_mode = transport_mode
