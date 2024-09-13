import sys
import time

from PySide6.QtCore import QObject, Signal

from mazegenerator.maze import Maze


class BfsLonghestPath(QObject):

    # Signals
    visiting = Signal(tuple)
    finished = Signal()

    def __init__(self, maze: Maze):
        super().__init__()

        self._maze = maze
        self.sleep = 0

    def run(self, sleep=0, start=None, absolute_longhest=True):
        """
            If absolute_longhest is True the algorithm finds the longest path in the maze,
            in that case the start cell is irrelevant.
            This is achieved applying the algorithm two times.
        """

        self.sleep = sleep

        # Initialize local attributes of the Maze
        for cell in self._maze:
            cell.distance = -1
            cell.set_visited(False)
            cell.prec = None

        # Init
        if start is None:
            start = self._maze.center()
        to_visit = []
        max_distance = 0
        max_distance_coord = ()
        to_visit.append(start)
        self._maze[start].distance = 0

        # BFS visit
        while len(to_visit) > 0:
            time.sleep(self.sleep)
            coord = to_visit.pop(0)
            if not self._maze[coord].is_visited():
                self._maze[coord].set_visited()
                if self.sleep > 0:
                    self.visiting.emit(coord)
                for neighbor_coord in self._maze.neighbors(coord, False):
                    distance = self._maze[coord].distance + 1
                    self._maze[neighbor_coord].distance = distance
                    self._maze[neighbor_coord].prec = coord

                    if distance > max_distance:
                        max_distance = distance
                        max_distance_coord = neighbor_coord
                    to_visit.append(neighbor_coord)

        if absolute_longhest:
            return self.run(sleep, max_distance_coord, False)
        else:
            # Calculate longest path
            path = []
            path.append(max_distance_coord)
            node = max_distance_coord
            while self._maze[node].prec is not None:
                node = self._maze[node].prec
                path.append(node)

            if self.sleep > 0:
                self.finished.emit(path)

            return path


if __name__ == '__main__':

    def display(coord, maze):
        print()
        if coord:
            print(f"Visiting {coord}")
        for row in range(0, maze.rows):
            for column in range(0, maze.columns):
                distance = maze[column, row].distance
                if distance >= 0:
                    sys.stdout.write(f'{distance: >6}')
                else:
                    sys.stdout.write(f'{".": >6}')
            sys.stdout.write('\n')

    def test():
        maze = Maze.from_str('Maze[6,6,5,9,5,1,3,9,12,14,12,12,7,10,4,3,10,6,1,9,12,5,3,11,12,12,12,6,9,7,10,12,6,11,6,3,3,10]')  # pylint: disable=line-too-long
        # maze = Maze.from_str('Maze[3, 1, 7, 3, 11]')

        # maze.print()
        # maze2 = Maze.from_str(maze.__repr__())
        # print(maze2)

        # print(maze.neighbors((0, 0)))
        # print(maze.neighbors((0, 0), False))
        # sys.exit(0)

        bfs = BfsLonghestPath(maze)
        bfs.visiting.connect(lambda coord: display(coord, maze))

        path = bfs.run()

        def fn_w(coord):
            if coord == path[0]:
                return '@'
            if coord == path[len(path) - 1]:
                return '#'
            if coord in path:
                return '*'
            return ' '

        maze.print(fn_w=fn_w)
        display(None, maze)
        print()
        print(path)

    test()
