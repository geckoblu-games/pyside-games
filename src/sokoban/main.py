from dataclasses import dataclass
import math
import sys

from PySide6.QtCore import Qt, QPoint, QEvent, QSettings
from PySide6.QtGui import QIcon, QPainter, QColor, QPen, QPixmap, QBrush, \
    QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsLineItem, QGraphicsRectItem, \
    QMessageBox

from sokoban import CELL_SIZE, Direction, next_point
from sokoban.chooseleveldialog import ChooseLevelDialog
from sokoban.levels import get_level, get_levels_count, get_sets
from sokoban.qgraphicsgrid import QGraphicsGridScene, QGraphicsGridView, QGraphicsGridPixmapItem, \
    QAutoCenterWidget, BoxItem, QGraphicsGridRectItem, PlayerItem
import sokoban.resources  # pylint: disable=unused-import

DEBUG = False
DRAW_GRID = False
PIXMAP_FLOOR = False

if DEBUG:
    VIEW_GRID_WIDTH = 15
    VIEW_GRID_HEIGHT = 8
else:
    VIEW_GRID_WIDTH = 21
    VIEW_GRID_HEIGHT = 15

WINDOW_WIDTH = VIEW_GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = VIEW_GRID_HEIGHT * CELL_SIZE

COLOR_BACKGROUND = QColor("#131926")
COLOR_GRAY = QColor("#333333")
COLOR_FLOOR = Qt.GlobalColor.darkGray


@dataclass
class Move:
    """Class for keeping track of player moves."""
    prev_player_pos: QPoint
    prev_box_pos: QPoint
    current_box_pos: QPoint

    def __init__(self, prev_player_pos: QPoint) -> None:
        self.prev_player_pos = prev_player_pos
        self.prev_box_pos = None
        self.current_box_pos = None


# TODO: A better separation of game logic and game drawing
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sokoban")
        self.setMinimumSize(WINDOW_WIDTH + 50, WINDOW_HEIGHT + 50)
        # self.setMaximumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # print("Window rect", self.size())
        self.move(0, 40)

        self.scene = QGraphicsGridScene()

        self.view = QGraphicsGridView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setInteractive(False)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setBackgroundBrush(COLOR_BACKGROUND)
        self.view.setStyleSheet("border: 0px")
        self.view.installEventFilter(self)
        # # self.view.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # # self.view.setMaximumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.view.setGridRect(0, 0, VIEW_GRID_WIDTH, VIEW_GRID_HEIGHT)
        # print("* View:  ", self.view.width(), self.view.height())

        self.setCentralWidget(QAutoCenterWidget(self.view))

        self.player = None
        self.level = None
        self.box_items = []
        self.history = []

        settings = QSettings()
        self.current_set = settings.value('level/set', get_sets()[0], str)
        self.current_level = settings.value('level/level', 0, int)
        self._new_level()

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue('level/set', self.current_set)
        settings.setValue('level/level', self.current_level)
        QMainWindow.closeEvent(self, event)

    def _new_level(self):
        self.scene.clear()
        self.history = []

        if self.current_level >= get_levels_count(self.current_set):
            self._show_setcompleted_dialog()
            self.current_level = 0
            return

        self.level = get_level(self.current_set, self.current_level)
        self.scene.setGridDimensions(self.level.columns, self.level.rows)

        if DRAW_GRID:
            self._draw_grid()
        self._draw_floor()
        self._draw_boxes()
        self._draw_goals()
        self._draw_player()

        self._center_view_on_player()

    def _draw_grid(self):
        """Draw the grid"""
        pen = QPen(COLOR_GRAY)
        pen.setWidth(1)
        for c in range(0, self.scene.gridHeight() + 1):
            line = QGraphicsLineItem(0, c * CELL_SIZE, self.scene.width(), c * CELL_SIZE)
            line.setPen(pen)
            self.scene.addItem(line)

        for c in range(0, self.scene.gridWidth() + 1):
            line = QGraphicsLineItem(c * CELL_SIZE, 0, c * CELL_SIZE, self.scene.height())
            line.setPen(pen)
            self.scene.addItem(line)

        rect = QGraphicsRectItem(0, 0, self.scene.width(), self.scene.height())
        pen = QPen(Qt.GlobalColor.blue)
        pen.setWidth(3)
        rect.setPen(pen)
        self.scene.addItem(rect)

    def _draw_floor(self):
        """Draw the floor"""
        wall_pixmap = QPixmap(":/images/wall.svg").scaled(CELL_SIZE, CELL_SIZE)
        ground_pixmap = QPixmap(":/images/ground.svg").scaled(CELL_SIZE, CELL_SIZE)

        for r in range(0, self.level.rows):
            for c in range(0, self.level.columns):
                if self.level.is_wall(c, r):
                    wall = QGraphicsGridPixmapItem(wall_pixmap)
                    wall.setGridPos(QPoint(c, r))
                    wall.setZValue(1)
                    self.scene.addItem(wall)
                else:
                    if self.level.is_inside(c, r):
                        if PIXMAP_FLOOR:
                            ground = QGraphicsGridPixmapItem(ground_pixmap)
                        else:
                            ground = QGraphicsGridRectItem(0, 0, CELL_SIZE, CELL_SIZE)
                            ground.setBrush(QBrush(COLOR_FLOOR))
                            ground.setPen(QPen(COLOR_FLOOR))
                        ground.setGridPos(QPoint(c, r))
                        ground.setZValue(0)
                        self.scene.addItem(ground)

    def _draw_boxes(self):
        """Draw the box items"""
        self.box_items = []
        for box_pos in self.level.boxes_start:
            box = BoxItem()
            box.setGridPos(box_pos)
            box.setZValue(2)
            box.setOnTarget(self.level.is_box_on_target(box_pos))
            self.box_items.append(box)
            self.scene.addItem(box)

    def _draw_goals(self):
        """Draw the goals"""
        goal_pixmap = QPixmap(":/images/goal.svg").scaled(CELL_SIZE, CELL_SIZE)
        for goal_pos in self.level.goals:
            goal = QGraphicsGridPixmapItem(goal_pixmap)
            goal.setGridPos(goal_pos)
            goal.setZValue(1)
            self.scene.addItem(goal)

    def _draw_player(self):
        """Draw the player"""
        self.player = PlayerItem()
        self.player.setGridPos(self.level.player_start)
        self.player.setZValue(100)
        self.scene.addItem(self.player)

    def _center_view_on_player(self):
        """Center the view on the player if the size of the level
            is bigger than the size of the view, on the view otherwise"""
        if self.level.columns > self.view.gridWidth():
            x1 = self.level.player_start.x() - int(self.view.gridWidth() / 2)
            x1 = max(0, x1)
            delta_x = x1 + self.view.gridWidth() - self.level.columns
            x1 = min(x1, x1 - delta_x)
            self.view.setGridX1(x1)
        else:
            frac, whole = math.modf((self.view.gridWidth() - self.level.columns) / 2)
            self.view.setXOffset(-frac)
            self.view.setGridX1(-int(whole))
        if self.level.rows > self.view.gridHeight():
            y1 = self.level.player_start.y() - int(self.view.gridHeight() / 2)
            y1 = max(0, y1)
            delta_y = y1 + self.view.gridHeight() - self.level.rows
            y1 = min(y1, y1 - delta_y)
            self.view.setGridY1(y1)
        else:
            frac, whole = math.modf((self.view.gridHeight() - self.level.rows) / 2)
            self.view.setYOffset(frac)
            self.view.setGridY1(-int(whole))

    def _shift_view(self, direction, next_position):
        x = next_position.x()
        y = next_position.y()
        if (direction == Direction.RIGHT and (self.view.gridX2() - x < 2) and
                (self.scene.gridWidth() - self.view.gridX2() > 1)):
            self.view.setGridX1(self.view.gridX1() + 1)
        elif (direction == Direction.LEFT and (x - self.view.gridX1() < 3) and
              (self.view.gridX1() > 0)):
            self.view.setGridX1(self.view.gridX1() - 1)
        elif (direction == Direction.DOWN and (self.view.gridY2() - y < 2) and
              (self.scene.gridHeight() - self.view.gridY2() > 1)):
            self.view.setGridY1(self.view.gridY1() + 1)
        elif (direction == Direction.UP and (y - self.view.gridY1() < 3) and
              (self.view.gridY1() > 0)):
            self.view.setGridY1(self.view.gridY1() - 1)

    def eventFilter(self, source, event):
        if source == self.view and event.type() == QEvent.KeyPress:
            key = event.key()
            self.handle_key_pressed(key)
            return True

        # Let the Window handle own events
        return super().eventFilter(source, event)

    def box_at(self, position):
        for box in self.box_items:
            if box.gridPos() == position:
                return box
        raise Exception("Box not found.")

    def handle_key_pressed(self, key):
        if key == Qt.Key_Left:
            # print("Key_Left")
            self._move_player(Direction.LEFT)
        elif key == Qt.Key_Right:
            self._move_player(Direction.RIGHT)
        elif key == Qt.Key_Up:
            self._move_player(Direction.UP)
        elif key == Qt.Key_Down:
            self._move_player(Direction.DOWN)
        elif key == Qt.Key_R:
            self._restart_level()
        elif key == Qt.Key_U:
            self._undo()
        elif key == Qt.Key_N:
            if self.current_level < get_levels_count(self.current_set) - 1:
                self.current_level += 1
                self._new_level()
        elif key == Qt.Key_P:
            if self.current_level > 0:
                self.current_level -= 1
                self._new_level()
        elif key == Qt.Key_Escape:
            self.show_choose_level_dialog()

    def _move_player(self, direction):

        # Here I don't check the level boundaries,
        # but every valid level is completely closed by walls
        next_position = next_point(self.player.gridPos(), direction)
        move = Move(self.player.gridPos())

        if self.level.is_wall(next_position):
            return
        if self.level.is_box(next_position):
            if self.level.can_push(next_position, direction):
                next_box_position = self.level.push_box(next_position, direction)
                box = self.box_at(next_position)
                box.setGridPos(next_box_position)
                box.setOnTarget(self.level.is_box_on_target(next_box_position))
                move.prev_box_pos = next_position
                move.current_box_pos = next_box_position
            else:
                return

        self.history.append(move)

        self._shift_view(direction, next_position)

        self.player.setGridPos(next_position)

        if self.level.is_level_completed():
            print("Level completed.")
            if self.current_level + 1 == get_levels_count(self.current_set):
                self._show_setcompleted_dialog()
            else:
                self._show_nextlevel_dialog()

    def _undo(self):
        if self.history:
            move = self.history.pop()
            self.player.setGridPos(move.prev_player_pos, True)
            if move.current_box_pos:
                box = self.box_at(move.current_box_pos)
                self.level.pull_box(move.current_box_pos, move.prev_box_pos)
                box.setGridPos(move.prev_box_pos)
                box.setOnTarget(self.level.is_box_on_target(move.prev_box_pos))

    def _show_nextlevel_dialog(self):
        button = QMessageBox.information(
            self,
            "Level completed",
            "\nDo you want to play next level?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.Yes,
        )
        if button == QMessageBox.StandardButton.Yes:
            self.current_level += 1
            self._new_level()

    def _show_setcompleted_dialog(self):
        QMessageBox.information(
            self,
            "Set Completed",
            "\nCongratulations\nYou played all the levels of the set.",
            buttons=QMessageBox.Ok,
            defaultButton=QMessageBox.Ok,
        )

    def _restart_level(self):
        button = QMessageBox.question(
            self,
            "Restart",
            "\nDo you really want to re-start the level?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.Yes,
        )
        if button == QMessageBox.StandardButton.Yes:
            self._new_level()

    def show_choose_level_dialog(self):
        dlg = ChooseLevelDialog(self, self.current_set, self.current_level)
        if dlg.exec():
            self.current_set, self.current_level = dlg.get_choice()
            self._new_level()


def main(app=None):

    QApplication.setWindowIcon(QIcon(":/images/icon.svg"))
    QApplication.setApplicationName("Sokoban")
    QApplication.setOrganizationDomain("geckoblu.net")
    QApplication.setOrganizationName("geckoblu")

    if not app:
        app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.show_choose_level_dialog()

    app.exec()


if __name__ == '__main__':
    main()
