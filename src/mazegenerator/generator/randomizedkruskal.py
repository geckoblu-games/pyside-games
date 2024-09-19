import random
import time
from typing import override

from mazegenerator import Direction
from mazegenerator.generator.abstractgenerator import AbstractGenerator
from mazegenerator.maze import Maze


class RandomizedKruskal(AbstractGenerator):

    def _get_randomized_set_of_walls(self):
        # Set of walls
        walls = []
        for row in range(0, self._maze.rows):
            # draw the north edge
            for column in range(0, self._maze.columns):
                # print(row, column)
                if row > 0:
                    walls.append(((column, row), Direction.NORTH))
                if column > 0:
                    walls.append(((column, row), Direction.WEST))
        random.shuffle(walls)

        return walls

    @override
    def run(self, sleep=0):

        self.sleep = sleep

        walls = self._get_randomized_set_of_walls()
        for i, cell in enumerate(self._maze):
            cell.cset = i

        self._running = True
        self._paused = False
        while walls and self._running:
            if self._paused:
                self._wait_for_unpause()

            coord1, direction = walls.pop()
            coord2 = self._maze.neighbor(coord1, direction)

            cset1 = self._maze[coord1].cset
            cset2 = self._maze[coord2].cset

            if cset1 != cset2:
                time.sleep(self.sleep)

                self._maze.crave_passage(coord1, coord2)

                for cell in self._maze:
                    if cell.cset == cset2:
                        cell.cset = cset1

                self._maze[coord1].set_visited()
                self._maze[coord2].set_visited()
                self.visited.emit(coord1)
                self.visited.emit(coord2)

        return len(walls) == 0


if __name__ == '__main__':

    def display(maze: Maze, _coord):
        print('')
        # print(f"Visiting: {coord}")
        maze.print()

    def test():
        print("start")

        maze = Maze(8, 8)

        maze.print()

        display_step = True

        alg = RandomizedKruskal(maze)
        if display_step:
            alg.visited.connect(lambda coord: display(maze, coord))

        alg.run(.2)

        # print(' ')
        # maze.print()

        # print(' ')
        print("end")

    test()
