from random import randint
import random
import sys
import time

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


def generate(maze: Maze, start_column=-1, start_row=-1):

    if start_column < 0 or start_column >= maze.columns:
        start_column = randint(0, maze.columns - 1)
    if start_row < 0 or start_row >= maze.rows:
        start_row = randint(0, maze.rows - 1)
    maze.start_column = start_column
    maze.start_row = start_row

    to_visit = []
    to_visit.append((None, (start_column, start_row)))
    # print(f"Starting from {to_visit[0]}")

    directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]

    while len(to_visit) > 0:
        from_coord, coord = to_visit.pop(0)
        if not maze[coord].is_visited():
            # print(f"Visiting: {coord}")
            maze[coord].set_visited()
            if from_coord:  # None just at the first step
                maze.crave_passage(from_coord, coord)
            yield
            random.shuffle(directions)
            for direction in directions:
                neighbor_coord = maze.neighbor(coord, direction)
                # print("\t", direction, neighbor_coord)
                if neighbor_coord and not maze[neighbor_coord].is_visited():  # can be None
                    to_visit.append((coord, neighbor_coord))
                else:
                    pass
                    # print(coord, direction, neighbor_coord)
        else:
            pass
            # print(f"\tSkipping: {coord}")


def display(maze: Maze):

    for row in range(0, maze.rows):

        # draw the north edge
        for column in range(0, maze.columns):
            if maze[(column, row)].has_wall(Direction.NORTH):
                sys.stdout.write('+---')
            else:
                sys.stdout.write('+   ')
        sys.stdout.write('+\n')

        # draw the west edge
        for column in range(0, maze.columns):
            if maze[(column, row)].has_wall(Direction.WEST):
                sys.stdout.write('|')
            else:
                sys.stdout.write(' ')
            if maze[(column, row)].is_visited():
                sys.stdout.write(' . ')
            else:
                sys.stdout.write(' # ')
        sys.stdout.write('|\n')

    # draw the bottom line
    print('+---' * maze.columns + '+')


if __name__ == '__main__':
    print("start")

    maz = Maze(8, 4)

    display_step = True

    for i in generate(maz, 0, 0):
        if display_step:
            print(' ')
            display(maz)
            time.sleep(.5)

    print(' ')
    display(maz)

    print(' ')
    print("end")
