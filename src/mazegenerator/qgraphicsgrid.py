from typing import overload

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem, \
    QGraphicsItem, QGraphicsRectItem

from mazegenerator import Direction

COLOR_NOT_VISITED_BACKGROUND = QColor("#131926")
COLOR_VISITED_BACKGROUND = Qt.GlobalColor.magenta
COLOR_VISITING_BACKGROUND = Qt.GlobalColor.yellow
COLOR_WALL = Qt.GlobalColor.black


class QGraphicsGridPItem():

    def __init__(self, cell_size, w_offset, h_offset):
        self.cell_size = cell_size
        self.w_offset = w_offset
        self.h_offset = h_offset

    @overload
    def setGridPos(self, position: QPoint) -> None:  # pylint: disable=no-self-use
        ...

    @overload
    def setGridPos(self, column: int, row: int) -> None:  # pylint: disable=no-self-use
        ...

    def setGridPos(self, column, row=None) -> None:
        if row is not None:
            x = self.cell_size * column + self.w_offset
            y = self.cell_size * row + self.h_offset
            QGraphicsItem.setPos(self, x, y)
        else:
            pos = column
            x = self.cell_size * pos.x() + self.w_offset
            y = self.cell_size * pos.y() + self.h_offset
            QGraphicsItem.setPos(self, x,)

    def gridPos(self) -> QPoint:
        pos = QGraphicsItem.pos(self)
        x = (pos.x() - self.w_offset) / self.cell_size
        y = (pos.y() - self.h_offset) / self.cell_size
        return QPoint(x, y)

    def setGridX(self, x: int) -> None:
        return QGraphicsItem.setX(self, x * self.cell_size + self.w_offset)

    def gridX(self) -> int:
        return (QGraphicsItem.x(self) - self.w_offset) / self.cell_size

    def setGridY(self, y: int) -> None:
        return QGraphicsItem.setY(self, y * self.cell_size + self.h_offset)

    def gridY(self) -> int:
        return (QGraphicsItem.y(self) - self.h_offset) / self.cell_size


class QGraphicsItemCell(QGraphicsItemGroup, QGraphicsGridPItem):

    def __init__(self, cell_size, w_offset, h_offset):
        QGraphicsItemGroup.__init__(self)
        QGraphicsGridPItem.__init__(self, cell_size, w_offset, h_offset)

        self.center = QGraphicsRectItem(0, 0, self.cell_size, self.cell_size)
        # self.center.setPos(50, 20)
        brush = QBrush(COLOR_NOT_VISITED_BACKGROUND)
        self.center.setBrush(brush)
        pen = QPen(COLOR_NOT_VISITED_BACKGROUND)
        pen.setWidth(2)
        # self.center.setPen(Qt.NoPen)
        self.center.setPen(pen)
        self.addToGroup(self.center)

        pen = QPen(COLOR_WALL)
        pen.setWidth(2)

        self.north_wall = QGraphicsLineItem(0, 0, self.cell_size, 0)
        self.north_wall.setPen(pen)
        self.addToGroup(self.north_wall)

        self.west_wall = QGraphicsLineItem(0, 0, 0, self.cell_size)
        self.west_wall.setPen(pen)
        self.addToGroup(self.west_wall)

        self.east_wall = QGraphicsLineItem(self.cell_size, 0, self.cell_size, self.cell_size)
        self.east_wall.setPen(pen)
        self.addToGroup(self.east_wall)
        # self.east_wall.setVisible(False)

        self.south_wall = QGraphicsLineItem(0, self.cell_size, self.cell_size, self.cell_size)
        self.south_wall.setPen(pen)
        self.addToGroup(self.south_wall)

        # self.reset()

    # def reset(self):
    #     self.walls = Direction.NORTH | Direction.SOUTH | Direction.EAST | Direction.WEST
    #     print(self.walls)

    def set_status(self, mazecell):
        if mazecell.is_visited():
            brush = QBrush(COLOR_VISITED_BACKGROUND)
            self.center.setBrush(brush)
            pen = QPen(COLOR_VISITED_BACKGROUND)
            pen.setWidth(2)
            # self.center.setPen(Qt.NoPen)
            self.center.setPen(pen)

        if not mazecell.has_wall(Direction.NORTH):
            self.north_wall.setVisible(False)

        if not mazecell.has_wall(Direction.WEST):
            self.west_wall.setVisible(False)

        if not mazecell.has_wall(Direction.EAST):
            self.east_wall.setVisible(False)

        if not mazecell.has_wall(Direction.SOUTH):
            self.south_wall.setVisible(False)

    def set_visiting(self, flag):
        if flag:
            brush = QBrush(COLOR_VISITING_BACKGROUND)
            self.center.setBrush(brush)
            pen = QPen(COLOR_VISITING_BACKGROUND)
            pen.setWidth(2)
            # self.center.setPen(Qt.NoPen)
            self.center.setPen(pen)
        else:
            brush = QBrush(COLOR_VISITED_BACKGROUND)
            self.center.setBrush(brush)
            pen = QPen(COLOR_VISITED_BACKGROUND)
            pen.setWidth(2)
            # self.center.setPen(Qt.NoPen)
            self.center.setPen(pen)
