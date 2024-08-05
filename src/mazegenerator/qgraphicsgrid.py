from typing import overload

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPen, QBrush
from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem, \
    QGraphicsItem, QGraphicsRectItem

from mazegenerator import CELL_SIZE, Direction


class QGraphicsGridPItem():

    @overload
    def setGridPos(self, position: QPoint) -> None:  # pylint: disable=no-self-use
        ...

    @overload
    def setGridPos(self, column: int, row: int) -> None:  # pylint: disable=no-self-use
        ...

    def setGridPos(self, column, row=None) -> None:
        if row is not None:
            QGraphicsItem.setPos(self, CELL_SIZE * column, CELL_SIZE * row)
        else:
            pos = column
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


class QGraphicsItemCell(QGraphicsItemGroup, QGraphicsGridPItem):

    def __init__(self):
        super().__init__()

        self.center = QGraphicsRectItem(0, 0, CELL_SIZE, CELL_SIZE)
        # self.center.setPos(50, 20)
        brush = QBrush(Qt.GlobalColor.red)
        self.center.setBrush(brush)
        pen = QPen(Qt.GlobalColor.red)
        pen.setWidth(2)
        # self.center.setPen(Qt.NoPen)
        self.center.setPen(pen)
        self.addToGroup(self.center)

        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(2)

        self.north_wall = QGraphicsLineItem(0, 0, CELL_SIZE, 0)
        self.north_wall.setPen(pen)
        self.addToGroup(self.north_wall)

        self.west_wall = QGraphicsLineItem(0, 0, 0, CELL_SIZE)
        self.west_wall.setPen(pen)
        self.addToGroup(self.west_wall)

        self.east_wall = QGraphicsLineItem(CELL_SIZE, 0, CELL_SIZE, CELL_SIZE)
        self.east_wall.setPen(pen)
        self.addToGroup(self.east_wall)
        # self.east_wall.setVisible(False)

        self.south_wall = QGraphicsLineItem(0, CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.south_wall.setPen(pen)
        self.addToGroup(self.south_wall)

        self.reset()

    def reset(self):
        self.walls = Direction.NORTH | Direction.SOUTH | Direction.EAST | Direction.WEST
        print(self.walls)