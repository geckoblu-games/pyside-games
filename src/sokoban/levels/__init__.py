from typing import overload

from PySide6.QtCore import QPoint

from sokoban import Direction, next_point

from sokoban.levels import microban
from sokoban.levels import sasquatch
from sokoban.levels import original_and_extra
from sokoban.levels import testlevels


class Level():

    def __init__(self, columns, rows, txtlevel):
        self.columns = columns
        self.rows = rows

        self.player_start = QPoint()
        self.floor = []
        self.boxes_start = []
        self.boxes = []
        self.goals = []
        self.reachables = []

        self.__parse_txtlevel(txtlevel)

    def __parse_txtlevel(self, txtlevel):
        for r, line in enumerate(txtlevel):
            floor = ''
            # for c in range(0, len(line)):
            for c, ch in enumerate(line):
                # Floor
                if ch == '#':
                    floor += '#'
                else:
                    floor += ' '

                # Player
                if ch in ['@', '+', 'P', 'p']:
                    self.player_start.setX(c)
                    self.player_start.setY(r)

                # boxs
                if ch in ['$', '*', 'B', 'b']:
                    self.boxes_start.append(QPoint(c, r))
                    self.boxes.append(QPoint(c, r))

                # Goals
                if ch in ['.', '*', '+', 'B', 'P']:
                    self.goals.append(QPoint(c, r))

            self.floor.append(floor.ljust(self.columns))

        self._build_reachables()

    @overload
    def is_wall(self, column: int, row: int) -> None:
        ...

    @overload
    def is_wall(self, position: QPoint) -> None:
        ...

    def is_wall(self, column, row=None):
        if isinstance(column, QPoint):
            position = column
            column = position.x()
            row = position.y()

        return self.floor[row][column] == '#'

    def is_box(self, position: QPoint) -> bool:
        return position in self.boxes

    def is_box_on_target(self, position: QPoint) -> bool:
        assert self.is_box(position), "Not a box"

        return position in self.goals

    def is_empty(self, position: QPoint) -> bool:
        return not self.is_wall(position) and not self.is_box(position)

    def can_push(self, position: QPoint, direction: Direction) -> bool:
        assert self.is_box(position), "Not a box"

        return self.is_empty(next_point(position, direction))

    def push_box(self, position: QPoint, direction: Direction) -> QPoint:
        assert self.is_box(position), "Not a box"

        next_position = next_point(position, direction)

        self.boxes.remove(position)
        self.boxes.append(next_position)

        return next_position

    def pull_box(self, current_position: QPoint, prev_position: QPoint) -> None:
        assert self.is_box(current_position), "Not a box"

        self.boxes.remove(current_position)
        self.boxes.append(prev_position)

    def is_level_completed(self):
        for box in self.boxes:
            if not box in self.goals:
                return False
        return True

    def is_inside(self, column, row):
        return QPoint(column, row) in self.reachables

    def _build_reachables(self):
        self.reachables = []

        self._visit(self.player_start)

    def _visit(self, point: QPoint):
        if point in self.reachables:
            return
        elif self.is_wall(point):
            return
        else:
            self.reachables.append(point)
            for neighbour in self._neighbours(point):
                self._visit(neighbour)

    def _neighbours(self, point):
        neighbours = []
        if point.x() > 0:
            neighbours.append(next_point(point, Direction.LEFT))
        if point.x() < self.columns - 1:
            neighbours.append(next_point(point, Direction.RIGHT))
        if point.y() > 0:
            neighbours.append(next_point(point, Direction.UP))
        if point.y() < self.rows - 1:
            neighbours.append(next_point(point, Direction.DOWN))
        return neighbours


@overload
def get_level(setname: str, ixd: int) -> Level:
    ...


@overload
def get_level(setname: str, levelname: str) -> Level:
    ...


def get_level(setname, levelkey):

    if isinstance(levelkey, int):
        levelname = list(_SETS[setname])[levelkey]
    else:
        levelname = levelkey

    txtlevel = _SETS[setname][levelname]

    rows = len(txtlevel)
    columns = 0
    for row in txtlevel:
        columns = max(columns, len(row))
    level = Level(columns, rows, txtlevel)

    return level


def get_levels_count(setname: str) -> int:
    return len(_SETS[setname])


def get_sets():
    return list(_SETS.keys())


_SETS = {}

# _SETS['microban'] = {}
#
# _SETS['microban']['l1'] = [
#         "    #####  ",
#         "    #   #",
#         "    #$  #",
#         "  ###  $##",
#         "  #  $ $ #",
#         "### # ## #   ######",
#         "#   # ## #####  ..#",
#         "# $  $          ..#",
#         "##### ### #@##  ..#",
#         "    #     #########",
#         "    #######"]
#

microban.append_set(_SETS)
sasquatch.append_set(_SETS)
original_and_extra.append_set(_SETS)
# testlevels.append_set(_SETS)
