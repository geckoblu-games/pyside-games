from enum import Enum

from PySide6.QtCore import QPoint

CELL_SIZE = 32


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 4


def find_first_last_occurrence(char, s):
    first = s.find(char)
    last = s.rfind(char)
    return first, last


def next_point(point: QPoint, direction: Direction) -> QPoint:
    if direction == Direction.RIGHT:
        return QPoint(point.x() + 1, point.y())
    elif direction == Direction.LEFT:
        return QPoint(point.x() - 1, point.y())
    elif direction == Direction.DOWN:
        return QPoint(point.x(), point.y() + 1)
    elif direction == Direction.UP:
        return QPoint(point.x(), point.y() - 1)

    # Impossible but just to silence pylin
    raise ValueError(f"Unknown direction: {direction}")
