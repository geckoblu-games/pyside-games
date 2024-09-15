import random
import sys

from PySide6.QtCore import Qt, QBasicTimer, QPoint, QEvent
from PySide6.QtGui import QIcon, QPainter, QBrush, QColor, QPen, QPixmap, QFont
from PySide6.QtWidgets import QGraphicsScene, QMainWindow, QGraphicsView, \
    QGraphicsRectItem, QGraphicsLineItem, QGraphicsPixmapItem, \
    QGraphicsSimpleTextItem, QMessageBox

import snake.resources  # pylint: disable=unused-import
from snake.enums import Direction, GameState

DEBUG = False

if DEBUG:
    GRID_WIDTH = 10
    GRID_HEIGHT = 10
else:
    GRID_WIDTH = 20  # 25
    GRID_HEIGHT = 15  # 20

CELL_SIZE = 32
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

FRUIT_POINTS = 10

COLOR_BACKGROUND = QColor("#131926")
COLOR_GRAY = QColor("#333333")

MOVE_TIME = 500  # millis


class QGraphicsGridPixmapItem(QGraphicsPixmapItem):

    def setGridPos(self, pos: QPoint) -> None:
        QGraphicsPixmapItem.setPos(self, CELL_SIZE * pos.x(), CELL_SIZE * pos.y())

    def gridPos(self) -> QPoint:
        pos = QGraphicsPixmapItem.pos(self)
        return QPoint(pos.x() / CELL_SIZE, pos.y() / CELL_SIZE)

    def setGridX(self, x: int) -> None:
        return QGraphicsPixmapItem.setX(self, x * CELL_SIZE)

    def gridX(self) -> int:
        return QGraphicsPixmapItem.x(self) / CELL_SIZE

    def setGridY(self, y: int) -> None:
        return QGraphicsPixmapItem.setY(self, y * CELL_SIZE)

    def gridY(self) -> int:
        return QGraphicsPixmapItem.y(self) / CELL_SIZE


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Snake")
        self.setWindowIcon(QIcon(':/qt-project.org/logos/pysidelogo.png'))
        # self.setWindowIcon(QIcon(QPixmap("./snakehead.png")))
        # TODO: Why +16 ?
        self.setMinimumSize(WINDOW_WIDTH + 16, WINDOW_HEIGHT + 16)
        # self.setMaximumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.move(100, 40)
        # print(self.iconSize())

        # Defining a scene rect of WINDOW_WIDTHxWINDOW_HEIGHT, with it's origin at 0,0.
        # If we don't set this on creation, we can set it later with .setSceneRect
        self.scene = QGraphicsScene(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

        # print(self.scene.size())

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setBackgroundBrush(COLOR_BACKGROUND)
        self.view.installEventFilter(self)

        rect = QGraphicsRectItem(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        pen = QPen(Qt.GlobalColor.darkBlue)
        pen.setWidth(3)
        rect.setPen(pen)

        pen = QPen(COLOR_GRAY)
        pen.setWidth(1)

        # Draw the grid
        for c in range(0, GRID_HEIGHT + 1):
            line = QGraphicsLineItem(0, c * CELL_SIZE, WINDOW_WIDTH, c * CELL_SIZE)
            line.setPen(pen)
            self.scene.addItem(line)
        for c in range(0, GRID_WIDTH + 1):
            line = QGraphicsLineItem(c * CELL_SIZE, 0, c * CELL_SIZE, WINDOW_HEIGHT)
            line.setPen(pen)
            self.scene.addItem(line)

        self.scene.addItem(rect)

        self.setCentralWidget(self.view)

        pixmap = QPixmap(":/images/snakehead.png")
        self.head = QGraphicsGridPixmapItem(pixmap)
        self.head.setZValue(100)  # Head always on top of other elements
        self.scene.addItem(self.head)

        pixmap = QPixmap(":/images/apple.png")
        self.fruit = QGraphicsGridPixmapItem(pixmap)
        self.fruit.setZValue(10)
        self.scene.addItem(self.fruit)

        self.score_label = QGraphicsSimpleTextItem("Points: 0")
        self.score_label.setBrush(QBrush(Qt.GlobalColor.darkGreen))
        # self.score_label.setPen(QPen(Qt.GlobalColor.black))
        # sansFont = QFont("", 16, QFont.Bold)
        sansfont = QFont("Sans", 14)
        self.score_label.setFont(sansfont)
        self.score_label.setZValue(200)
        self.scene.addItem(self.score_label)

        self.body = []
        self.game_state = GameState.RUNNING
        self.direction = random.choice(list(Direction))
        self.future_direction = None
        self.score = 0

        self._start_new_game()

    def _start_new_game(self):

        for body_segment in self.body:
            self.scene.removeItem(body_segment)

        self.game_state = GameState.RUNNING
        self.direction = random.choice(list(Direction))
        self.future_direction = None
        self.body = []
        self.score = 0

        head_position = QPoint(random.randrange(0, GRID_WIDTH),
                               random.randrange(0, GRID_HEIGHT))
        self.head.setGridPos(head_position)

        fruit_position = self.random_free_position()
        self.fruit.setGridPos(fruit_position)

        self._update_score()

        if DEBUG:
            self.head.setGridPos(QPoint(5, 3))
            self.fruit.setGridPos(QPoint(8, 3))
            self.direction = Direction.RIGHT
            body_positions = []
            body_positions.append(QPoint(4, 3))
            body_positions.append(QPoint(3, 3))
            body_positions.append(QPoint(2, 3))
            body_positions.append(QPoint(1, 3))
            body_positions.append(QPoint(0, 3))
            for position in body_positions:
                snake_segment = QGraphicsGridPixmapItem(QPixmap(":/images/snakebody.png"))
                snake_segment.setGridPos(position)
                self.scene.addItem(snake_segment)
                self.body.append(snake_segment)

        self.timer = QBasicTimer()
        self._start_timer()

    def _update_score(self):
        self.score_label.setText(f"Points: {self.score}")
        rect = self.score_label.boundingRect()
        x = WINDOW_WIDTH - CELL_SIZE / 3 - rect.width()
        y = WINDOW_HEIGHT - CELL_SIZE / 4 - rect.height()
        self.score_label.setPos(x, y)

    def random_free_position(self):
        free_pos = []
        for y in range(0, GRID_HEIGHT):
            for x in range(0, GRID_WIDTH):
                p = QPoint(x, y)
                if p != self.head.gridPos() and not self._in_body(p):
                    free_pos.append(p)

        return random.choice(free_pos)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():

            # Move the body
            if self.body:
                next_position = QPoint(self.head.gridPos())
                for body_segment in self.body:
                    position = body_segment.gridPos()
                    body_segment.setGridPos(next_position)
                    next_position = position
                # tail_position is used later if the snake eat a fruit
                tail_position = position
            else:
                # if the body is empty, the first segment will grow from the fruit position
                tail_position = self.fruit.gridPos()

            if self.future_direction is not None:
                self.direction = self.future_direction
                self.future_direction = None

            head_position = self._next_head_position()

            self.head.setGridPos(head_position)

            if head_position == self.fruit.gridPos():
                # The snake eat a fruit
                self.eat_fruit(tail_position)
            else:
                # Check if the snake is eating itself
                if self.body and self._in_body(head_position):
                    self._show_gameover_dialog()

        else:
            super().timerEvent(event)

    def eat_fruit(self, tail_position):
        self.timer.stop()
        self._start_timer()

        body_semgent = QGraphicsGridPixmapItem(QPixmap(":/images/snakebody.png"))
        body_semgent.setGridPos(tail_position)
        self.scene.addItem(body_semgent)
        self.body.append(body_semgent)

        self.score += FRUIT_POINTS
        self.fruit.setGridPos(self.random_free_position())

        self._update_score()

    def eventFilter(self, source, event):
        if source == self.view and event.type() == QEvent.KeyPress:
            key = event.key()
            self.handle_key_pressed(key)

        # Let the Window handle own events
        return super().eventFilter(source, event)

    def handle_key_pressed(self, key):
        # RUNNING
        if self.game_state == GameState.RUNNING:
            if key == Qt.Key_Left and self.direction != Direction.RIGHT:
                self.future_direction = Direction.LEFT
            elif key == Qt.Key_Right and self.direction != Direction.LEFT:
                self.future_direction = Direction.RIGHT
            elif key == Qt.Key_Up and self.direction != Direction.DOWN:
                self.future_direction = Direction.UP
            elif key == Qt.Key_Down and self.direction != Direction.UP:
                self.future_direction = Direction.DOWN

            if key in (Qt.Key_P, Qt.Key_Space):
                self.game_state = GameState.PAUSED
                self.timer.stop()

            if key == Qt.Key_Q:
                self._show_quitting_dialog()

        # PAUSED
        elif self.game_state == GameState.PAUSED:
            if key in (Qt.Key_P, Qt.Key_Space):
                self.game_state = GameState.RUNNING
                self._start_timer()

            if key == Qt.Key_Q:
                self._show_quitting_dialog()

    def _next_head_position(self):
        head_position = self.head.gridPos()
        if self.direction == Direction.DOWN:
            head_position.setY(head_position.y() + 1)
            if head_position.y() >= GRID_HEIGHT:
                head_position.setY(0)
        elif self.direction == Direction.UP:
            head_position.setY(head_position.y() - 1)
            if head_position.y() < 0:
                head_position.setY(GRID_HEIGHT - 1)
        elif self.direction == Direction.RIGHT:
            head_position.setX(head_position.x() + 1)
            if head_position.x() >= GRID_WIDTH:
                head_position.setX(0)
        elif self.direction == Direction.LEFT:
            head_position.setX(head_position.x() - 1)
            if head_position.x() < 0:
                head_position.setX(GRID_WIDTH - 1)

        return head_position

    def _start_timer(self):
        self.timer.start(MOVE_TIME - self.score, self)

    def _in_body(self, position):
        return any(body_segment.gridPos() == position for body_segment in self.body)

# contain_position =
#    lambda body, position: bool(any(body_segment.gridPos() == position for body_segment in body))

    def _show_quitting_dialog(self):
        prec_state = self.game_state
        self.game_state = GameState.QUITTING
        self.timer.stop()
        button = QMessageBox.critical(
            self,
            "Quitting ...",
            "Do you really want to quit?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.Yes,
        )
        if button == QMessageBox.StandardButton.Yes:
            sys.exit(0)
        else:
            self.game_state = prec_state
            if self.game_state == GameState.RUNNING:
                self._start_timer()

    def _show_gameover_dialog(self):
        self.game_state = GameState.GAMEOVER
        self.timer.stop()
        button = QMessageBox.critical(
            self,
            "Game over",
            f"Your score is {self.score}\n\nDo you want to play again?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.Yes,
        )
        if button == QMessageBox.StandardButton.No:
            sys.exit(0)
        else:
            self._start_new_game()
