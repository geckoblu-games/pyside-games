from enum import Enum


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 4

    def opposite(self):
        if self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP
        elif self == Direction.LEFT:
            return Direction.RIGHT
        elif self == Direction.RIGHT:
            return Direction.LEFT

        # Should never happen
        raise ValueError("Unhandled direction")


class GameState(Enum):
    STARTING = 1
    RUNNING = 2
    PAUSED = 3
    GAMEOVER = 4
    QUITTING = 5
