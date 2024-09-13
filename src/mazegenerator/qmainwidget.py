from enum import Enum
import sys
import traceback

from PySide6.QtCore import Qt, QMargins, QRunnable, Slot, QObject, Signal, \
    QThreadPool
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox, \
    QPushButton, QSpinBox, QGraphicsLineItem, QStyle, QCheckBox

from mazegenerator.bfslonghestpath import BfsLonghestPath
from mazegenerator.generator import randomizeddepthfirst
from mazegenerator.generator.randomizeddepthfirst import RandomizedDepthFirst
from mazegenerator.qgraphicsgrid import QGraphicsItemCell


class RunningStatus(Enum):
    RUNNING = 1
    TERMINATED = 2
    PAUSED = 4


_DEFAULT_W = 45
_DEFAULT_H = 35
_DEFAULT_SPEED = 50

# _DEFAULT_W = 8
# _DEFAULT_H = 8
# _DEFAULT_SPEED = 0


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

        right_widget = self._get_rigth_widget()

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
        self._worker = None

        self._running_status = RunningStatus.TERMINATED
        self._set_status(self._running_status)
        self.from_visiting = None
        self._init_maze()

    def _get_rigth_widget(self) -> QWidget:
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

        self.checkbox_longestpath = QCheckBox("Show longest path")
        self.checkbox_longestpath.setChecked(True)
        layout.addWidget(self.checkbox_longestpath, 3, 0)

        layout.addWidget(QLabel("Size:"), 4, 0)
        self.spinbox_w = QSpinBox()
        self.spinbox_w.setMinimum(3)
        self.spinbox_w.setMaximum(100)
        self.spinbox_w.setValue(_DEFAULT_W)
        # self.spinbox_w.setEnabled(False)
        self.spinbox_w.valueChanged.connect(self._init_maze)
        self.spinbox_h = QSpinBox()
        self.spinbox_h.setMinimum(3)
        self.spinbox_h.setMaximum(100)
        self.spinbox_h.setValue(_DEFAULT_H)
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
        layout.addWidget(wdg, 5, 0)

        layout.addWidget(QLabel("Speed:"), 6, 0)
        self.spinbox_speed = QSpinBox()
        self.spinbox_speed.setMinimum(0)
        self.spinbox_speed.setMaximum(1000)
        self.spinbox_speed.setSingleStep(10)
        self.spinbox_speed.setValue(_DEFAULT_SPEED)
        self.spinbox_speed.valueChanged.connect(self._speed_changed)
        layout.addWidget(self.spinbox_speed, 7, 0)

        # Just to fill the space
        layout.addWidget(QWidget(), 8, 0)
        layout.setRowStretch(8, 1)

        layout.addWidget(self._get_controls_widget(), 9, 0)

        layout.addWidget(QLabel(), 10, 0)

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

    def _get_controls_widget(self) -> QWidget:
        controll_widget = QWidget()
        controll_widget.setAutoFillBackground(True)

        layout = QGridLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(0)

        pixmapi = QStyle.SP_MediaPlay
        icon = self.style().standardIcon(pixmapi)
        self.start_button = QPushButton(icon, '')  # pylint: disable=attribute-defined-outside-init
        self.start_button.clicked.connect(self._start)
        layout.addWidget(self.start_button, 0, 0)

        pixmapi = QStyle.SP_MediaPause
        icon = self.style().standardIcon(pixmapi)
        self.pause_button = QPushButton(icon, '')  # pylint: disable=attribute-defined-outside-init
        self.pause_button.clicked.connect(self._pause)
        layout.addWidget(self.pause_button, 0, 1)

        pixmapi = QStyle.SP_MediaStop
        icon = self.style().standardIcon(pixmapi)
        self.stop_button = QPushButton(icon, '')  # pylint: disable=attribute-defined-outside-init
        self.stop_button.clicked.connect(self._stop)
        layout.addWidget(self.stop_button, 0, 2)

        controll_widget.setLayout(layout)
        return controll_widget

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

    def _set_status(self, status: RunningStatus):
        self._running_status = status
        if status == RunningStatus.TERMINATED:
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.spinbox_w.setEnabled(True)
            self.spinbox_h.setEnabled(True)
            self.combobox.setEnabled(True)
            self.checkbox_longestpath.setEnabled(True)
        elif status == RunningStatus.RUNNING:
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.spinbox_w.setEnabled(False)
            self.spinbox_h.setEnabled(False)
            self.combobox.setEnabled(False)
            self.checkbox_longestpath.setEnabled(False)
        elif status == RunningStatus.PAUSED:
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.spinbox_w.setEnabled(False)
            self.spinbox_h.setEnabled(False)
            self.combobox.setEnabled(False)
            self.checkbox_longestpath.setEnabled(False)

    def _speed_changed(self):
        speed = self._get_speed()

        if self._worker:
            self._worker.set_speed(speed)

    def _get_speed(self):
        speed = self.spinbox_speed.value()
        if speed <= 1:
            speed = 1
        speed = speed / 1000.0
        return speed

    def _start(self):
        if self._running_status == RunningStatus.TERMINATED:
            self._set_status(RunningStatus.RUNNING)
            self._init_maze()

            # Here is a long-running process, in this case I can solve it with just a Timer,
            # but I want to try a WorkerThreads
            speed = self._get_speed()
            self._worker = Worker(self.maze, speed)
            self._worker.signals.processing.connect(self._display)
            self._worker.signals.visiting.connect(self._visiting)
            self._worker.signals.finished.connect(self._worker_finished)
            self.threadpool.start(self._worker)
        elif self._running_status == RunningStatus.PAUSED:
            self._set_status(RunningStatus.RUNNING)
            self._worker.pause(False)

    def _pause(self):
        if self._running_status == RunningStatus.RUNNING:
            self._set_status(RunningStatus.PAUSED)
            self._worker.pause(True)
        elif self._running_status == RunningStatus.PAUSED:
            self._set_status(RunningStatus.RUNNING)
            self._worker.pause(False)

    def _stop(self):
        self._set_status(RunningStatus.TERMINATED)
        if self._worker:
            self._worker.stop()

    def _worker_finished(self):
        self._worker = None
        self._set_status(RunningStatus.TERMINATED)

        if self.from_visiting:
            column, row = self.from_visiting
            self.cells[self.maze.columns * row + column].set_visiting(False)
            self.from_visiting = None

        print()
        print(self.maze)

        if self.checkbox_longestpath.isChecked():
            bfs = BfsLonghestPath(self.maze)
            path = bfs.run()
            print(f'BFS: {path}')
            print(f'     lenght: {len(path)}')
            for coord in path:
                self.cells[self.maze.columns * coord[1] + coord[0]].set_in_path()
            coord = path[0]
            self.cells[self.maze.columns * coord[1] + coord[0]].set_start_path()
            coord = path[len(path) - 1]
            self.cells[self.maze.columns * coord[1] + coord[0]].set_end_path()

    def _display(self, processing):
        from_coord, coord = processing
        column, row = coord
        self.cells[self.maze.columns * row + column].set_status(self.maze[coord])
        if self.from_visiting == coord:
            self.cells[self.maze.columns * row + column].set_visiting(True)
        if from_coord:
            column, row = from_coord
            self.cells[self.maze.columns * row + column].set_status(self.maze[from_coord])

    def _visiting(self, visiting):
        column, row = visiting
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
        self._alg = None

    @Slot()
    def run(self):
        try:
            self._alg = RandomizedDepthFirst(self._maze)
            self._alg.visiting.connect(self.signals.visiting.emit)
            self._alg.processing.connect(self.signals.processing.emit)
            self._alg.run(self._speed)

            # for step in randomizeddepthfirst.generate(self.maze, 0, 0):
            #     self.signals.progress.emit(step)
            #     time.sleep(self.speed)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()  # Done

    @Slot(int)
    def set_speed(self, speed):
        self._speed = speed
        if self._alg:
            self._alg.sleep = speed

    @Slot()
    def pause(self, flag):
        if self._alg:
            self._alg.pause(flag)

    @Slot()
    def stop(self):
        if self._alg:
            self._alg.stop()


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
