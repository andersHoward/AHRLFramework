class SYS_Mover():
    def __init__(self, mover_component, transform_component):
        pass

    def player_move_or_attack(dx, dy):
        global fov_recompute, L_entities

        # Coordinates the entity is trying to act upon.
        x = player.x + dx
        y = player.y + dy

        # Try to find attackable entity at target tile.
        target = None
        for entity in L_entities:
            if entity.fighter and entity.x == x and entity.y == y:
                target = entity
                break

        # Attack if entity found, else move
        if target is not None:
            player.fighter.attack(target)
        else:
            player.move(dx, dy)
            fov_recompute = True


    # Move by the given amount.
    def Try_Move(self, dx, dy):
        if not is_blocked(self.x + dx,
                          self.y + dy):  # Check if the tile we're trying to move into is a blocking tile or contains a blocking object.
            self.x += dx
            self.y += dy


    # Moves object towards a target location. Normally used for simple AI.
    def move_towards(self, target_x, target_y):
        # Get vector.
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normalize to a unit vector (of 1), then round to int so movement is restricted to the grid, then move.
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)
