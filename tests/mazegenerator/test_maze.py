from mazegenerator.maze import Maze


class TestMaze:

    def setup_method(self):
        print()

    def test_repr_(self):
        maze1 = Maze(2, 2)
        repr1 = repr(maze1)
        print(repr1)

        assert repr1 == 'Maze[2,2,15,15,15,15]'

    def test_from_str(self):
        maze1 = Maze(6, 6)
        repr1 = repr(maze1)
        print(repr1)

        maze2 = Maze.from_str(repr1)
        repr2 = repr(maze2)
        print(repr2)

        assert repr1 == repr2
