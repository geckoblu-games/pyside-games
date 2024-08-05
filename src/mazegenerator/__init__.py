from enum import Enum, IntFlag, auto

from PySide6.QtGui import QColor


CELL_SIZE = 16

COLOR_BACKGROUND = QColor("#131926")  

class CellStatus(Enum):
    NORMAL = 1
    VISITING = 2
    VISITED = 4
    
class Direction(IntFlag):
    NORTH = 1
    SOUTH = 2
    WEST = 4
    EAST = 8

