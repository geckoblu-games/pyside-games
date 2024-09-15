from PySide6.QtCore import QMargins, QPoint
from PySide6.QtGui import QPalette, QColor, QPixmap
from PySide6.QtWidgets import QWidget, QGridLayout, QGraphicsPixmapItem, \
    QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem

from sokoban import CELL_SIZE


class QAutoCenterWidget(QWidget):

    def __init__(self, widget):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#131926'))
        self.setPalette(palette)

        layout = QGridLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSpacing(0)
        layout.addWidget(QWidget(), 0, 0)
        layout.addWidget(QWidget(), 2, 2)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(2, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(2, 1)
        layout.addWidget(widget, 1, 1)

        self.setLayout(layout)


class QGraphicsGridPItem():

    def setGridPos(self, pos: QPoint) -> None:
        QGraphicsItem.setPos(self, CELL_SIZE * pos.x(), CELL_SIZE * pos.y())

    def gridPos(self) -> QPoint:
        pos = QGraphicsItem.pos(self)
        return QPoint(pos.x() / CELL_SIZE, pos.y() / CELL_SIZE)

    def setGridX(self, x: int) -> None:
        return QGraphicsItem.setX(self, x * CELL_SIZE)

    def gridX(self) -> int:
        return QGraphicsItem.x(self) / CELL_SIZE

    def setGridY(self, y: int) -> None:
        return QGraphicsItem.setY(self, y * CELL_SIZE)

    def gridY(self) -> int:
        return QGraphicsItem.y(self) / CELL_SIZE


class QGraphicsGridPixmapItem(QGraphicsPixmapItem, QGraphicsGridPItem):
    pass


class QGraphicsGridRectItem(QGraphicsRectItem, QGraphicsGridPItem):
    pass


class BoxItem(QGraphicsGridPixmapItem):

    def __init__(self):
        super().__init__()
        self.box_pixmap = QPixmap(":/images/box.svg").scaled(CELL_SIZE, CELL_SIZE)
        self.box_on_target_pixmap = QPixmap(":/images/box_on_target.png").scaled(CELL_SIZE, CELL_SIZE)
        self.setPixmap(self.box_pixmap)

    def setOnTarget(self, flag: bool) -> None:
        # print("Box is on target:", flag)
        if flag:
            self.setPixmap(self.box_on_target_pixmap)
        else:
            self.setPixmap(self.box_pixmap)


class PlayerItem(QGraphicsGridPixmapItem):

    def __init__(self):
        super().__init__()
        self.movecount = 0
        self.player_pixmas = []
        self.player_pixmas.append(QPixmap(":/images/player_right_1.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_right_2.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_right_1.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_right_3.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_left_1.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_left_2.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_left_1.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_left_3.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_down_1.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_down_2.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_down_1.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_down_3.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_up_1.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_up_2.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_up_1.svg").scaled(CELL_SIZE, CELL_SIZE))
        self.player_pixmas.append(QPixmap(":/images/player_up_3.svg").scaled(CELL_SIZE, CELL_SIZE))

    def setGridPos(self, pos: QPoint, undo: bool=False) -> None:
        prec_pos = self.gridPos()
        if not undo:
            if pos.x() > prec_pos.x():
                direction = 0  # right
            elif pos.x() < prec_pos.x():
                direction = 1  # left
            elif pos.y() > prec_pos.y():
                direction = 2  # down
            elif pos.y() < prec_pos.y():
                direction = 3  # up
        else:
            # walking backwards
            if pos.x() > prec_pos.x():
                direction = 1  # right
            elif pos.x() < prec_pos.x():
                direction = 0  # left
            elif pos.y() > prec_pos.y():
                direction = 3  # down
            elif pos.y() < prec_pos.y():
                direction = 2  # up

        pixmap = self.player_pixmas[self.movecount + direction * 4]

        self.setPixmap(pixmap)
        self.movecount += 1
        if self.movecount > 3:
            self.movecount = 0
        super().setGridPos(pos)


class QGraphicsGridScene(QGraphicsScene):

    def __init__(self):
        super().__init__()

        self._width = 0
        self._height = 0

    def setGridDimensions(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self.setSceneRect(0, 0, width * CELL_SIZE, height * CELL_SIZE)

    def gridWidth(self) -> int:
        return self._width

    def gridHeight(self) -> int:
        return self._height


class QGraphicsGridView(QGraphicsView):

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)

        self._x1 = 0
        self._y1 = 0
        self._width = 0
        self._height = 0
        self._xoffset = 0
        self._yoffset = 0

    def setGridRect(self, x1: int, y1: int, width: int, height: int) -> None:
        self._x1 = x1
        self._y1 = y1
        self._width = width
        self._height = height

        self._updateView()

    def gridX1(self) -> int:
        return self._x1

    def gridY1(self) -> int:
        return self._y1

    def setGridX1(self, x1: int) -> None:
        self._x1 = x1
        self._updateView()

    def setGridY1(self, y1: int) -> None:
        self._y1 = y1
        self._updateView()

    def gridX2(self) -> int:
        return self._x1 + self._width - 1

    def gridY2(self) -> int:
        return self._y1 + self._height - 1

    def gridWidth(self) -> int:
        return self._width

    def gridHeight(self) -> int:
        return self._height

    def setXOffset(self, xoffset):
        self._xoffset = xoffset
        self._updateView()

    def xOffset(self):
        return self._xoffset

    def setYOffset(self, yoffset):
        self._yoffset = yoffset
        self._updateView()

    def yOffset(self):
        return self._yoffset

    def _updateView(self):
        x = (self._xoffset + self._x1) * CELL_SIZE
        y = (self._yoffset + self._y1) * CELL_SIZE
        # print("_updateView", x, y)
        w = self._width * CELL_SIZE
        h = self._height * CELL_SIZE
        self.setSceneRect(x, y, w, h)
        self.ensureVisible(x, y, w, h)
