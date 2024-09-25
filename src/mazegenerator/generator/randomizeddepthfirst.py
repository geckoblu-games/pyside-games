import random
import sys
import time
from typing import override

from mazegenerator import Direction
from mazegenerator.generator.abstractgenerator import AbstractGenerator
from mazegenerator.maze import Maze


class RandomizedDepthFirst(AbstractGenerator):

    @override
    def run(self, sleep=0) -> bool:

        self.sleep = sleep

        to_visit = []
        coord = (self._maze.start_column, self._maze.start_row)
        to_visit.append((None, coord))
        self.tovisit.emit(coord)

        self._running = True
        self._paused = False
        while len(to_visit) > 0 and self._running:
            if self._paused:
                self._wait_for_unpause()

            from_coord, coord = to_visit.pop(0)

            if not self._maze[coord].is_visited():
                self.visiting.emit(coord)

                time.sleep(self.sleep)

                self._maze[coord].set_visited()

                if from_coord:  # None just at the first step
                    self._maze.crave_passage(from_coord, coord)

                neighbors = self._maze.neighbors(coord, False)  # choose a random direction
                random.shuffle(neighbors)
                for neighbor in neighbors:
                    to_visit.insert(0, (coord, neighbor))  # push at the end (FIFO)
                    self.tovisit.emit(neighbor)

                self._maze[coord].set_visited()
                self.visited.emit(coord)

        return len(to_visit) == 0


if __name__ == '__main__':

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
