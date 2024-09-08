from mazegenerator import Direction


class MazeCell:

    def __init__(self):
        self.visited = False
        self.walls = Direction.NORTH | Direction.SOUTH | Direction.EAST | Direction.WEST

    def is_visited(self) -> bool:
        return self.visited

    def set_visited(self):
        self.visited = True

    def has_wall(self, direction: Direction) -> bool:
        # print(self.walls & direction > 0)
        return self.walls & direction > 0

    def remove_wall(self, direction: Direction):
        self.walls &= ~direction


class Maze:

    def __init__(self, columns: int, rows: int):
        self.columns = columns
        self.rows = rows
        self.start_column = -1
        self.start_row = -1

        self.cells = [MazeCell() for _ in range(rows * columns)]

    def __getitem__(self, coord):
        column, row = coord
        return self.cells[self.columns * row + column]

    def neighbor(self, coord: (int, int), direction: Direction) -> (int, int):
        column, row = coord
        if direction == Direction.NORTH and row > 0:
            return (column, row - 1)
        if direction == Direction.SOUTH and row < self.rows - 1:
            return (column, row + 1)
        if direction == Direction.WEST and column > 0:
            return (column - 1, row)
        if direction == Direction.EAST and column < self.columns - 1:
            return (column + 1, row)
        return None

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
