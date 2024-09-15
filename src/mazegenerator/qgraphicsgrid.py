from enum import Enum
from typing import overload

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem, \
    QGraphicsItem, QGraphicsRectItem

from mazegenerator import Direction

COLOR_NOT_VISITED_BACKGROUND = QColor('#131926')
COLOR_TOVISIT_BACKGROUND = QColor('#5252ba')
COLOR_VISITING_BACKGROUND = QColor('#c8eddd')
COLOR_VISITED_BACKGROUND = QColor('#5488d0')
COLOR_INPATH_BACKGROUND = COLOR_VISITED_BACKGROUND.lighter(120)
COLOR_WALL = QColor(Qt.GlobalColor.black)
COLOR_START_OF_PATH = QColor(Qt.GlobalColor.darkGreen)
COLOR_END_OF_PATH = QColor(Qt.GlobalColor.darkRed)


class CellStatus(Enum):
    NOTVISITED = 0
    TOVISIT = 1
    VISITING = 2
    VISITED = 4


class QGraphicsGridPItem():

    # I don't know the reason but this is called twice,
    # first time automatically with no parameters, so the need for default values,
    # second time manually by QGraphicsItemCell.__init__ with the correct values
    def __init__(self, cell_size=0, w_offset=0, h_offset=0):
        self.cell_size = cell_size
        self.w_offset = w_offset
        self.h_offset = h_offset

    @overload
    def setGridPos(self, position: QPoint) -> None:
        ...

    @overload
    def setGridPos(self, column: int, row: int) -> None:
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
        # TODO: I don't know the reason but QGraphicsGridPItem.__init__ is called twice
        #       first time automatically with no parameters,
        #       second time manually  with the correct values
        QGraphicsItemGroup.__init__(self)
        QGraphicsGridPItem.__init__(self, cell_size, w_offset, h_offset)

        self._status = CellStatus.NOTVISITED

        self.center = QGraphicsRectItem(0, 0, self.cell_size, self.cell_size)
        self.addToGroup(self.center)
        self._set_cell_color(COLOR_NOT_VISITED_BACKGROUND)

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

        self.south_wall = QGraphicsLineItem(0, self.cell_size, self.cell_size, self.cell_size)
        self.south_wall.setPen(pen)
        self.addToGroup(self.south_wall)

    def _set_cell_color(self, color):
        brush = QBrush(color)
        self.center.setBrush(brush)
        pen = QPen(color)
        pen.setWidth(2)
        # self.center.setPen(Qt.NoPen)
        self.center.setPen(pen)

    def set_status(self, mazecell, status: CellStatus):

        self._status = status

        if self._status == CellStatus.TOVISIT:
            self._set_cell_color(COLOR_TOVISIT_BACKGROUND)
        elif self._status == CellStatus.VISITING:
            self._set_cell_color(COLOR_VISITING_BACKGROUND)
        elif self._status == CellStatus.VISITED:
            self._set_cell_color(COLOR_VISITED_BACKGROUND)

        if not mazecell.has_wall(Direction.NORTH):
            self.north_wall.setVisible(False)

        if not mazecell.has_wall(Direction.WEST):
            self.west_wall.setVisible(False)

        if not mazecell.has_wall(Direction.EAST):
            self.east_wall.setVisible(False)

        if not mazecell.has_wall(Direction.SOUTH):
            self.south_wall.setVisible(False)

    def set_in_path(self):
        brush = QBrush(COLOR_INPATH_BACKGROUND)
        self.center.setBrush(brush)
        pen = QPen(COLOR_INPATH_BACKGROUND)
        pen.setWidth(2)
        self.center.setPen(pen)

    def set_start_path(self):
        brush = QBrush(COLOR_START_OF_PATH)
        self.center.setBrush(brush)
        pen = QPen(COLOR_START_OF_PATH)
        pen.setWidth(2)
        self.center.setPen(pen)

    def set_end_path(self):
        brush = QBrush(COLOR_END_OF_PATH)
        self.center.setBrush(brush)
        pen = QPen(COLOR_END_OF_PATH)
        pen.setWidth(2)
        self.center.setPen(pen)
