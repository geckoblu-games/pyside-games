from random import randint
import time

from PySide6.QtCore import QObject, Signal

from mazegenerator.maze import Maze


class AbstractGenerator(QObject):

    # Signals
    tovisit = Signal(tuple)
    visiting = Signal(tuple)
    visited = Signal(tuple)

    def __init__(self, maze: Maze, start_column=-1, start_row=-1, start_at_random=False):
        super().__init__()

        self._maze = maze

        if start_column < 0 or start_column >= maze.columns:
            if start_at_random:
                start_column = randint(0, maze.columns - 1)
            else:
                start_column = int(maze.columns / 2)
        if start_row < 0 or start_row >= maze.rows:
            if start_at_random:
                start_row = randint(0, maze.rows - 1)
            else:
                start_row = int(maze.rows / 2)

        self._maze.start_column = start_column
        self._maze.start_row = start_row
        self.sleep = 0
        self._running = False
        self._paused = False

    def run(self, sleep=0) -> bool:
        raise NotImplementedError('To be implemented.')

    def stop(self):
        self._running = False
        self._paused = False

    def pause(self, flag):
        self._paused = flag

    def _wait_for_unpause(self):
        while self._paused:
            time.sleep(.01)
