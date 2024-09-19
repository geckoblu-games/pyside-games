
import random
import time
from typing import override

from mazegenerator.generator.abstractgenerator import AbstractGenerator
from mazegenerator.maze import Maze


class RandomizedBreadthFirst(AbstractGenerator):

    @override
    def run(self, sleep=0):

        self.sleep = sleep
        to_visit = []
        coord = (self._maze.start_column, self._maze.start_row)
        to_visit.append((None, coord))
        self.tovisit.emit(coord)

        # directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]

        self._running = True
        self._paused = False
        while len(to_visit) > 0 and self._running:
            if self._paused:
                self._wait_for_unpause()

            # The core point is to choose a random element from the frontier
            # TODO: swap before pop?
            from_coord, coord = to_visit.pop(random.randrange(len(to_visit)))

            if not self._maze[coord].is_visited():
                self.visiting.emit(coord)

                time.sleep(self.sleep)

                if from_coord:  # None just at the first step
                    self._maze.crave_passage(from_coord, coord)

                for neighbor in self._maze.neighbors(coord, False):
                    to_visit.append((coord, neighbor))  # doesn't matter where I insert, I pop randomly
                    self.tovisit.emit(neighbor)

                self._maze[coord].set_visited()
                self.visited.emit(coord)

        return len(to_visit) == 0


if __name__ == '__main__':

    def display(maze: Maze, coord):
        print('')
        print(f"Visiting: {coord}")
        maze.print()

    def test():
        print("start")

        maze = Maze(8, 6)

        display_step = True

        alg = RandomizedBreadthFirst(maze)
        if display_step:
            alg.visiting.connect(lambda coord: display(maze, coord))

        alg.run(.2)

        print(' ')
        maze.print()

        print(' ')
        print("end")

    test()
