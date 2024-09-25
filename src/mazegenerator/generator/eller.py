import random
import time
from typing import override

from mazegenerator.generator.abstractgenerator import AbstractGenerator
from mazegenerator.maze import Maze


class Eller(AbstractGenerator):
    # pylint: disable=line-too-long
    """
    Create the first row. No cells will be members of any set

    Join any cells not members of a set to their own unique set

    For any row:
        1. Moving from left to right:
            If the current cell and the cell to the right are members of the same set do nothing
            If the current cell and the cell to the right are members of different set:
                Randomly decide to crave a passage or not to the right (for the last row of the maze 'randomly' became 'always')
            If you decide to crave a passage, union the sets to which the current cell and the cell to the right are members.
            
        2. Moving again from left to right: 
            Randomly decide to crave a passage or not to the south.
            Make sure that each set has at least one cell without a bottom-wall (This prevents isolations)
         
         3. Prepare for the next row   
    """

    @override
    def run(self, sleep=0):
        """Generate a maze using Eller's algorithm."""

        self.sleep = sleep

        row_sets = [0] * self._maze.columns
        next_row_sets = [0] * self._maze.columns
        next_set_id = 1

        self._running = True
        self._paused = False

        for r in range(self._maze.rows):
            next_set_id = self._generate_ids(row_sets, next_set_id)

            # Step 1: Merge adjacent cells in the row randomly
            self._merge_cells_in_row(r, row_sets)
            if not self._running:
                return False
            if self._paused:
                self._wait_for_unpause()

            # Step 2: Create vertical connections for each set
            self._create_vertical_connections(r, row_sets, next_row_sets)

            # Step 3: Prepare for the next row
            row_sets = next_row_sets[:]
            next_row_sets = [0] * self._maze.columns

        return r == self._maze.rows - 1

    def _generate_ids(self, row_sets, next_set_id):
        """Assign IDs to the current row cells if they don't have one"""
        for c in range(self._maze.columns):
            if row_sets[c] == 0:
                row_sets[c] = next_set_id
                next_set_id += 1
        return next_set_id

    def _merge_cells_in_row(self, r, row_sets):
        """ Merge adjacent cells in the row randomly """
        for c in range(self._maze.columns - 1):
            set1 = row_sets[c]
            set2 = row_sets[c + 1]
            # if set differs, merge randomly or always if we are on the last line
            if set1 != set2 and (random.choice([True, False]) or r == self._maze.rows - 1):
                self._maze.crave_passage((c, r), (c + 1, r))
                for k in range(c + 1, self._maze.columns):
                    if row_sets[k] == set2:
                        row_sets[k] = set1  # Merge sets
            self.visited.emit((c, r))
            time.sleep(self.sleep)
            if not self._running:
                return
            if self._paused:
                self._wait_for_unpause()

        # Last cell in the row could be considered visited
        self.visited.emit((c + 1, r))
        time.sleep(self.sleep)

    def _create_vertical_connections(self, r, row_sets, next_row_sets):
        """Create vertical connections for each set"""
        if r < self._maze.rows - 1:  # Skip vertical connections if it's the last row
            set_all = set()
            set_used = set()
            for c in range(self._maze.columns):
                set_all.add(row_sets[c])
                # Ramdomly crave vertical passage
                if random.choice([True, False]):
                    self._maze.crave_passage((c, r), (c, r + 1))
                    next_row_sets[c] = row_sets[c]
                    set_used.add(row_sets[c])

            # Make sure that each set has at least one cell without a bottom-wall
            diff = set_all.difference(set_used)
            if diff:
                for set1 in diff:
                    cset = []
                    for c in range(self._maze.columns):
                        if row_sets[c] == set1:
                            cset.append(c)

                    c = random.choice(cset)
                    self._maze.crave_passage((c, r), (c, r + 1))
                    next_row_sets[c] = row_sets[c]


if __name__ == '__main__':

    def display(maze: Maze, _coord):
        print('')
        # print(f"Visiting: {coord}")
        maze.print()

    def test():
        print("start")

        maze = Maze(8, 8)

        maze.print()

        display_step = False

        alg = Eller(maze)
        if display_step:
            alg.visited.connect(lambda coord: display(maze, coord))

        alg.run(0)

        print(' ')
        maze.print()

        # print(' ')
        print("end")

    test()
