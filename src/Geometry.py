#  _____                           _
# |  __ \                         | |
# | |  \/ ___  ___  _ __ ___   ___| |_ _ __ _   _
# | | __ / _ \/ _ \| '_ ` _ \ / _ \ __| '__| | | |
# | |_\ \  __/ (_) | | | | | |  __/ |_| |  | |_| |
#  \____/\___|\___/|_| |_| |_|\___|\__|_|   \__, |
#                                            __/ |
#                                           |___/
#
'''Classes used to help create shapes, e.g. on the UI, or parts of the map.'''
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Rect:
    '''Rect: A rectangle on the map; used to characterize a room.'''
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        return(self.x1 <= other.x2 and self.x2 >= other.x1 and
               self.y1 <= other.y2 and self.y2 >= other.y1)