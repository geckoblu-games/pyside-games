import sys

from mazegenerator import Direction

_HEADER_LEN = 2


class _MazeCell:

    def __init__(self):
        self._visited = False
        self._walls = Direction.NORTH | Direction.SOUTH | Direction.EAST | Direction.WEST

    def is_visited(self) -> bool:
        return self._visited

    def set_visited(self, flag=True):
        self._visited = flag

    def has_wall(self, direction: Direction) -> bool:
        # print(self._walls & direction > 0)
        return self._walls & direction > 0

    def remove_wall(self, direction: Direction):
        self._walls &= ~direction


class Maze:

    def __init__(self, columns: int, rows: int):
        self._columns = columns
        self._rows = rows

        # self._start = (-1, -1)
        # self._finish = (-1, -1)

        self._cells = [_MazeCell() for _ in range(rows * columns)]

    def __getitem__(self, coord):
        column, row = coord
        return self._cells[self._columns * row + column]

    def __iter__(self):
        for cell in self._cells:
            yield cell

    @property
    def columns(self):
        return self._columns

    @property
    def rows(self):
        return self._rows

    # @property
    # def start(self) -> (int, int):
    #     return self._start
    #
    # @start.setter
    # def start(self, value):
    #     pass
    #
    # @property
    # def finish(self) -> (int, int):
    #     return self._finish
    #
    # @finish.setter
    # def finish(self, value):
    #     pass

    def center(self):
        start_column = int(self._columns / 2)
        start_row = int(self._rows / 2)
        return (start_column, start_row)

    def neighbor(self, coord: (int, int), direction: Direction) -> (int, int):
        column, row = coord
        if direction == Direction.NORTH and row > 0:
            return (column, row - 1)
        if direction == Direction.SOUTH and row < self._rows - 1:
            return (column, row + 1)
        if direction == Direction.WEST and column > 0:
            return (column - 1, row)
        if direction == Direction.EAST and column < self._columns - 1:
            return (column + 1, row)
        return None

    def neighbors(self, coord: (int, int), include_visited=True):
        column, row = coord
        neighbors = []
        if row > 0 and (include_visited or not self[column, row - 1].is_visited()):
            neighbors.append((column, row - 1))
        if row < self._rows - 1 and (include_visited or not self[column, row + 1].is_visited()):
            neighbors.append((column, row + 1))
        if column > 0 and (include_visited or not self[column - 1, row].is_visited()):
            neighbors.append((column - 1, row))
        if column < self._columns - 1 and (include_visited or not self[column + 1, row].is_visited()):
            neighbors.append((column + 1, row))
        return neighbors

    def visitable_neighbors(self, coord: (int, int), include_visited=True):
        column, row = coord
        neighbors = []
        if row > 0 and not self[column, row].has_wall(Direction.NORTH) \
                   and (include_visited or not self[column, row - 1].is_visited()):
            neighbors.append((column, row - 1))
        if row < self._rows - 1 and not self[column, row].has_wall(Direction.SOUTH) \
                               and (include_visited or not self[column, row + 1].is_visited()):
            neighbors.append((column, row + 1))
        if column > 0 and not self[column, row].has_wall(Direction.WEST) \
                      and (include_visited or not self[column - 1, row].is_visited()):
            neighbors.append((column - 1, row))
        if column < self._columns - 1 and not self[column, row].has_wall(Direction.EAST)\
                                     and (include_visited or not self[column + 1, row].is_visited()):
            neighbors.append((column + 1, row))
        return neighbors

    def crave_passage(self, from_coord, to_coord):
        fc, fr = from_coord
        tc, tr = to_coord
        if fc == tc:
            if fr < tr:
                self[from_coord].remove_wall(Direction.SOUTH)
                self[to_coord].remove_wall(Direction.NORTH)
                return
            if fr > tr:
                self[from_coord].remove_wall(Direction.NORTH)
                self[to_coord].remove_wall(Direction.SOUTH)
                return
        else:
            if fc < tc:
                self[from_coord].remove_wall(Direction.EAST)
                self[to_coord].remove_wall(Direction.WEST)
                return
            if fc > tc:
                self[from_coord].remove_wall(Direction.WEST)
                self[to_coord].remove_wall(Direction.EAST)
                return

    def print(self, fn_w=lambda _coord: ' '):  # pylint: disable=too-many-branches

        # First row
        for row in range(0, self._rows):
            # draw the north edge
            for column in range(0, self._columns):
                if column == 0 and row == 0:
                    sys.stdout.write('╔═══')
                elif row == 0:
                    if self[(column, row)].has_wall(Direction.WEST):
                        sys.stdout.write('╤═══')
                    else:
                        sys.stdout.write('════')
                else:
                    # row > 0 -----------------------------
                    if column == 0:
                        if self[(column, row)].has_wall(Direction.NORTH):
                            sys.stdout.write('╟')
                        else:
                            sys.stdout.write('║')
                    else:
                        self._print_flag(column, row)

                    if self[(column, row)].has_wall(Direction.NORTH):
                        sys.stdout.write('───')
                    else:
                        sys.stdout.write('   ')
            if row == 0:
                sys.stdout.write('╗\n')
            else:
                if self[(self._columns - 1, row)].has_wall(Direction.NORTH):
                    sys.stdout.write('╢\n')
                else:
                    sys.stdout.write('║\n')

            # draw the west edge
            for column in range(0, self._columns):
                if self[(column, row)].has_wall(Direction.WEST):
                    if column == 0:
                        sys.stdout.write('║')
                    else:
                        sys.stdout.write('|')
                else:
                    sys.stdout.write(' ')
                # if self[(column, row)].is_visited():
                #     sys.stdout.write('   ')
                # else:
                sys.stdout.write(f' {fn_w((column, row))} ')
            sys.stdout.write('║\n')

        # draw the bottom line
        sys.stdout.write('╚═══')
        for column in range(1, self._columns):
            if self[(column, self._rows - 1)].has_wall(Direction.WEST):
                sys.stdout.write('╧═══')
            else:
                sys.stdout.write('════')
        print('╝')

    def _print_flag(self, column, row):  # pylint: disable=too-many-branches
        # row > 0 and column > 0 ----------
        flag = 0
        if self[(column, row)].has_wall(Direction.NORTH):
            flag += 1
        if self[(column - 1, row)].has_wall(Direction.NORTH):
            flag += 10
        if self[(column, row)].has_wall(Direction.WEST):
            flag += 100
        if self[(column, row - 1)].has_wall(Direction.WEST):
            flag += 1000

        if flag == 1:
            sys.stdout.write('╶')
        elif flag == 10:
            sys.stdout.write('╴')
        elif flag == 11:
            sys.stdout.write('─')
        elif flag == 100:
            sys.stdout.write('╷')
        elif flag == 101:
            sys.stdout.write('┌')
        elif flag == 110:
            sys.stdout.write('┐')
        elif flag == 111:
            sys.stdout.write('┬')
        elif flag == 1000:
            sys.stdout.write('╵')
        elif flag == 1001:
            sys.stdout.write('└')
        elif flag == 1010:
            sys.stdout.write('┘')
        elif flag == 1011:
            sys.stdout.write('┴')
        elif flag == 1100:
            sys.stdout.write('|')
        elif flag == 1101:
            sys.stdout.write('├')
        elif flag == 1110:
            sys.stdout.write('┤')
        elif flag == 1111:
            sys.stdout.write('┼')
        else:
            raise ValueError(f"Unexpected flag: {flag}")

    def __repr__(self):
        rpr = f'Maze[{self._columns},{self._rows}'  # ,{self.start[1]},{self.start[2]}'
        for cell in self._cells:
            rpr += f',{cell._walls}'
        rpr += ']'
        return rpr

    @staticmethod
    def from_str(s):
        assert s.startswith('Maze['), 'Not a valid source string for a Maze'
        assert s.endswith(']'), 'Not a valid source string for a Maze'
        i1 = s.find('[') + 1  # pylint: disable=invalid-name
        i2 = s.find(']')  # pylint: disable=invalid-name
        l = s[i1: i2].split(',')  # pylint: disable=invalid-name
        l = [int(x) for x in l]  # pylint: disable=invalid-name
        assert len(l) > _HEADER_LEN, 'Not a valid source string for a Maze'
        columns = l[0]
        rows = l[1]
        assert len(l) == (columns * rows + _HEADER_LEN), 'Not a valid source string for a Maze'

        maze = Maze(columns, rows)
        # maze.start = (l[2], l[3])

        for i, cell in enumerate(maze._cells):  # pylint: disable=protected-access
            cell._walls = Direction(l[i + _HEADER_LEN])  # pylint: disable=protected-access

        return maze
