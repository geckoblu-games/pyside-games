from random import randint
import random
import sys
import time

from PySide6.QtCore import QObject, Signal

from mazegenerator import Direction
from mazegenerator.maze import Maze


class RandomizedDepthFirst(QObject):

    # Signals
    visiting = Signal(tuple)
    processing = Signal(tuple)

    def __init__(self, maze: Maze, start_column=-1, start_row=-1,
                 start_at_center=True, start_at_random=False, depthfirst=True):
        super().__init__()

        self._depthfirst = depthfirst
        self._maze = maze

        if start_column < 0 or start_column >= maze.columns:
            if start_at_center:
                start_column = int(maze.columns / 2)
            elif start_at_random:
                start_column = randint(0, maze.columns - 1)
            else:
                raise Exception(f"Invalid start_colum: {start_column}")
        if start_row < 0 or start_row >= maze.rows:

            if start_at_center:
                start_row = int(maze.rows / 2)
            elif start_at_random:
                start_row = randint(0, maze.rows - 1)
            else:
                raise Exception(f"Invalid start_colum: {start_column}")

        self._maze.start_column = start_column
        self._maze.start_row = start_row
        self.sleep = 0

    def run(self, sleep=0):

        self.sleep = sleep
        to_visit = []
        to_visit.append((None, (self._maze.start_column, self._maze.start_row)))
        # print(f"Starting from {to_visit[0]}")

        directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]

        step = -1
        while len(to_visit) > 0:
            time.sleep(self.sleep)
            from_coord, coord = to_visit.pop(0)
            self.visiting.emit(coord)
            if not self._maze[coord].is_visited():
                self._maze[coord].set_visited()
                if from_coord:  # None just at the first step
                    self._maze.crave_passage(from_coord, coord)
                step += 1
                self.processing.emit((from_coord, coord))
                # yield (from_coord, coord)
                random.shuffle(directions)
                for direction in directions:
                    neighbor_coord = self._maze.neighbor(coord, direction)
                    # print("\t", direction, neighbor_coord)
                    if neighbor_coord and not self._maze[neighbor_coord].is_visited():  # can be None
                        if self._depthfirst:
                            # depth first: append at the top
                            to_visit.insert(0, (coord, neighbor_coord))
                        else:
                            # breadth first: append at the end
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
                sys.stdout.write('   ')
            else:
                sys.stdout.write(' # ')
        sys.stdout.write('|\n')

    # draw the bottom line
    print('+---' * maze.columns + '+')
    print()


if __name__ == '__main__':

    def test():
        print("start")

        maze = Maze(8, 6)

        display_step = True

        alg = RandomizedDepthFirst(maze, 0, 0)
        # alg.visiting.connect(lambda coord: print(f"Visiting: {coord}"))
        if display_step:
            alg.visiting.connect(lambda coord: display(maze))

        alg.run(.2)

        # for step in generate(maze, 0, 0, depthfirst=True):
        #     if display_step:
        #         print(' ')
        #         display(maze)
        #         time.sleep(.2)

        print(' ')
        display(maze)

        print(' ')
        print("end")

    test()
