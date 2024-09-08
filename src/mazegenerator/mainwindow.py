from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPalette
from PySide6.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsView

from mazegenerator import CELL_SIZE, MAZE_COLUMNS, MAZE_ROWS
from mazegenerator.qmainwidget import QMainWidget

#
# DEBUG = False
#
# if DEBUG:
#     VIEW_GRID_WIDTH = 15
#     VIEW_GRID_HEIGHT = 8
# else:
#     VIEW_GRID_WIDTH = 90
#     VIEW_GRID_HEIGHT = 50
#
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 650

SCENE_WIDTH = MAZE_COLUMNS * CELL_SIZE
SCENE_HEIGHT = MAZE_ROWS * CELL_SIZE


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Maze Generator")
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # self.setMaximumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.move(300, 20)

        print(SCENE_WIDTH, SCENE_HEIGHT)
        self.scene = QGraphicsScene(0, 0, SCENE_WIDTH, SCENE_HEIGHT)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setInteractive(False)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.view.setBackgroundBrush(COLOR_BACKGROUND)
        self.view.setStyleSheet("border: 0px")
        self.view.installEventFilter(self)
        # # self.view.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # # self.view.setMaximumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.view.setSceneRect(-1, -1, SCENE_WIDTH, SCENE_HEIGHT)

        palette = self.palette()
        self.view.setBackgroundBrush(palette.color(QPalette.Window))

        self.setCentralWidget(QMainWidget(self.scene, self.view))

        # print("Window:", self.size())
        # print("Scene:", self.scene.sceneRect())
        # print("View:", self.view.size())
        # print("View:", self.view.sceneRect())

        # cell = QGraphicsItemCell()
        # cell.setGridPos(10, 10)
        # self.scene.addItem(cell)

        # for row in range(0, MAZE_ROWS):
        #     for column in range(0, MAZE_COLUMNS):
        #         cell = QGraphicsItemCell()
        #         cell.setGridPos(column, row)
        #         self.scene.addItem(cell)
