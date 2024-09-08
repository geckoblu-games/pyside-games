import sys
import traceback

from PySide6.QtCore import Qt, QMargins, QRunnable, Slot, QObject, Signal, \
    QThreadPool
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox, \
    QPushButton, QSpinBox, QGraphicsLineItem

from mazegenerator.generator import randomizeddepthfirst
from mazegenerator.generator.randomizeddepthfirst import RandomizedDepthFirst
from mazegenerator.qgraphicsgrid import QGraphicsItemCell


class QMainWidget(QWidget):

    def __init__(self, scene, view):
        super().__init__()
        self.setAutoFillBackground(True)

        self.scene = scene
        self.view = view

        # palette = self.palette()
        # palette.setColor(QPalette.Window, QColor('#131926'))
        # palette.setColor(QPalette.Window, Qt.GlobalColor.red)
        # self.setPalette(palette)

        left_widget = self._get_left_widget(view)

        right_widget = self._get_rith_widget()

        layout = QGridLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(0)
        layout.addWidget(left_widget, 0, 0)
        layout.addWidget(right_widget, 0, 1)
        layout.setColumnStretch(0, 1)
        # layout.setColumnStretch(1, 1)
        self.setLayout(layout)

        self.threadpool = QThreadPool()
        # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.worker = None

        self._init_maze()

    def _get_rith_widget(self) -> QWidget:
        right_widget = QWidget()
        right_widget.setAutoFillBackground(True)
        # palette = right_widget.palette()
        # palette.setColor(QPalette.Window, Qt.GlobalColor.yellow)
        # right_widget.setPalette(palette)

        layout = QGridLayout()
        right_widget.setLayout(layout)

        layout.addWidget(QLabel(), 0, 0)  # Empty line

        layout.addWidget(QLabel("Algorithm:"), 1, 0)
        self.combobox = QComboBox()
        self.combobox.addItems(["Randomized depth-first", "Two", "Three"])
        layout.addWidget(self.combobox, 2, 0)

        layout.addWidget(QLabel("Size:"), 3, 0)
        self.spinbox_w = QSpinBox()
        self.spinbox_w.setMinimum(3)
        self.spinbox_w.setMaximum(100)
        self.spinbox_w.setValue(45)
        # self.spinbox_w.setEnabled(False)
        self.spinbox_w.valueChanged.connect(self._init_maze)
        self.spinbox_h = QSpinBox()
        self.spinbox_h.setMinimum(3)
        self.spinbox_h.setMaximum(100)
        self.spinbox_h.setValue(35)
        # self.spinbox_h.setEnabled(False)
        self.spinbox_h.valueChanged.connect(self._init_maze)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(0, 0, 0, 0))
        # layout2.setSpacing(0)
        layout2.addWidget(QLabel("W:"), 0, 0)
        layout2.addWidget(self.spinbox_w, 0, 1)
        layout2.addWidget(QLabel("H:"), 0, 2)
        layout2.addWidget(self.spinbox_h, 0, 3)
        layout2.addWidget(QWidget(), 0, 4)
        layout2.setColumnStretch(4, 1)
        wdg = QWidget()
        wdg.setLayout(layout2)
        layout.addWidget(wdg, 4, 0)

        layout.addWidget(QLabel("Speed:"), 5, 0)
        self.spinbox_speed = QSpinBox()
        self.spinbox_speed.setMinimum(0)
        self.spinbox_speed.setMaximum(1000)
        self.spinbox_speed.setSingleStep(10)
        self.spinbox_speed.setValue(50)
        self.spinbox_speed.valueChanged.connect(self._speed_changed)
        layout.addWidget(self.spinbox_speed, 6, 0)

        # Just to fill the space
        layout.addWidget(QWidget(), 7, 0)
        layout.setRowStretch(7, 1)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self._start)
        layout.addWidget(self.start_button, 8, 0)

        layout.addWidget(QLabel(), 9, 0)

        return right_widget

    def _get_left_widget(self, view) -> QWidget:
        left_widget = QWidget()
        # left_widget.setAutoFillBackground(True)
        # palette = left_widget.palette()
        # palette.setColor(QPalette.Window, Qt.GlobalColor.green)
        # left_widget.setPalette(palette)

        layout = QGridLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(0)
        # layout.addWidget(QWidget(), 0, 0)
        # layout.addWidget(QWidget(), 2, 2)
        # layout.setColumnStretch(0, 1)
        # layout.setColumnStretch(2, 1)
        # layout.setRowStretch(0, 1)
        # layout.setRowStretch(2, 1)
        layout.addWidget(view, 1, 1)

        left_widget.setLayout(layout)

        return left_widget

    def _init_maze(self):
        self.from_visiting = None
        self.scene.clear()

        scene_width = self.scene.sceneRect().width()
        scene_height = self.scene.sceneRect().height()

        # Perimeter
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(2)
        line = QGraphicsLineItem(0, 0, scene_width, 0)
        line.setPen(pen)
        self.scene.addItem(line)
        line = QGraphicsLineItem(scene_width, 0, scene_width, scene_height)
        line.setPen(pen)
        self.scene.addItem(line)
        line = QGraphicsLineItem(0, scene_height, scene_width, scene_height)
        line.setPen(pen)
        self.scene.addItem(line)
        line = QGraphicsLineItem(0, 0, 0, scene_height)
        line.setPen(pen)
        self.scene.addItem(line)

        h = self.spinbox_h.value()
        w = self.spinbox_w.value()

        self.maze = randomizeddepthfirst.Maze(w, h)

        max_cell_width = int(scene_width / self.maze.columns)
        max_cell_heigth = int(scene_height / self.maze.rows)
        cell_size = min(max_cell_width, max_cell_heigth)
        w_offset = int((scene_width - self.maze.columns * cell_size) / 2)
        h_offset = int((scene_height - self.maze.rows * cell_size) / 2)

        self.cells = []
        for row in range(0, self.maze.rows):
            for column in range(0, self.maze.columns):

                cell = QGraphicsItemCell(cell_size, w_offset, h_offset)
                cell.setGridPos(column, row)
                self.scene.addItem(cell)
                self.cells.append(cell)

    def _set_enabled(self, flag):
        self.start_button.setEnabled(flag)
        self.spinbox_w.setEnabled(flag)
        self.spinbox_h.setEnabled(flag)
        self.combobox.setEnabled(flag)

    def _speed_changed(self):
        speed = self._get_speed()

        if self.worker:
            self.worker.set_speed(speed)

    def _get_speed(self):
        speed = self.spinbox_speed.value()
        if speed <= 1:
            speed = 1
        speed = speed / 1000.0
        return speed

    def _start(self):
        # print("start")
        self._set_enabled(False)

        self._init_maze()

        # Here is a long-running process, in this case I can solve with just a Timer,
        # but I want to try a WorkerThreads
        speed = self._get_speed()
        self.worker = Worker(self.maze, speed)
        self.worker.signals.processing.connect(self._display)
        self.worker.signals.visiting.connect(self._visiting)
        self.worker.signals.finished.connect(self._worker_finished)
        self.threadpool.start(self.worker)

        # for step in randomizeddepthfirst.generate(maze, 0, 0, depthfirst=True):
        #     print(f"step {step}")
        #     self._display(maze)
        #     # time.sleep(speed)
        #     if step > 200: break
        #
        # print("stop")

    def _worker_finished(self):
        self.worker = None
        self._set_enabled(True)

        if self.from_visiting:
            column, row = self.from_visiting
            self.cells[self.maze.columns * row + column].set_visiting(False)
            self.from_visiting = None

    def _display(self, processing):
        # print(f's{coord2}')
        # for row in range(0, self.maze.rows):
        #     for column in range(0, self.maze.columns):
        #         self.cells[self.maze.columns * row + column].set_status(self.maze[(column, row)])
        # print(f'e{step}\n')
        from_coord, coord = processing
        column, row = coord
        self.cells[self.maze.columns * row + column].set_status(self.maze[coord])
        if self.from_visiting == coord:
            self.cells[self.maze.columns * row + column].set_visiting(True)
        if from_coord:
            column, row = from_coord
            self.cells[self.maze.columns * row + column].set_status(self.maze[from_coord])
        # self.from_visiting = coord

    def _visiting(self, visiting):
        column, row = visiting
        # self.cells[self.maze.columns * row + column].set_status(self.maze[coord])
        self.cells[self.maze.columns * row + column].set_visiting(True)
        if self.from_visiting:
            column, row = self.from_visiting
            self.cells[self.maze.columns * row + column].set_visiting(False)
        self.from_visiting = visiting


class Worker(QRunnable):

    def __init__(self, maze, speed):
        super(Worker, self).__init__()

        self.signals = WorkerSignals()

        self._maze = maze
        self._speed = speed
        self.alg = None

    @Slot()
    def run(self):
        try:
            self.alg = RandomizedDepthFirst(self._maze)
            self.alg.visiting.connect(self.signals.visiting.emit)
            self.alg.processing.connect(self.signals.processing.emit)
            self.alg.run(self._speed)

            # for step in randomizeddepthfirst.generate(self.maze, 0, 0):
            #     self.signals.progress.emit(step)
            #     time.sleep(self.speed)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()  # Done

    def set_speed(self, speed):
        self._speed = speed
        if self.alg:
            self.alg.sleep = speed


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    # result = Signal(object)
    visiting = Signal(tuple)
    processing = Signal(tuple)
