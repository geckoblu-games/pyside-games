from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, \
    QComboBox, QSpinBox


class QMainWidget(QWidget):

    def __init__(self, view):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        # palette.setColor(QPalette.Window, QColor('#131926'))
        # palette.setColor(QPalette.Window, Qt.GlobalColor.red)
        self.setPalette(palette)

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

    def _get_rith_widget(self) -> QWidget:
        right_widget = QWidget()
        right_widget.setAutoFillBackground(True)
        # palette = right_widget.palette()
        # palette.setColor(QPalette.Window, Qt.GlobalColor.yellow)
        # right_widget.setPalette(palette)

        layout = QGridLayout()
        right_widget.setLayout(layout)

        layout.addWidget(QLabel("Algorithm:"), 0, 0)
        combobox = QComboBox()
        combobox.addItems(["Randomized depth-first", "Two", "Three"])
        layout.addWidget(combobox, 1, 0)

        layout.addWidget(QLabel("Size:"), 2, 0)
        spinbox_w = QSpinBox()
        spinbox_w.setMinimum(3)
        spinbox_w.setMaximum(100)
        spinbox_w.setEnabled(False)
        spinbox_h = QSpinBox()
        spinbox_h.setMinimum(3)
        spinbox_h.setMaximum(100)
        spinbox_h.setEnabled(False)
        layout2 = QGridLayout()
        layout2.setContentsMargins(QMargins(0, 0, 0, 0))
        # layout2.setSpacing(0)
        layout2.addWidget(QLabel("W:"), 0, 0)
        layout2.addWidget(spinbox_w, 0, 1)
        layout2.addWidget(QLabel("H:"), 0, 2)
        layout2.addWidget(spinbox_h, 0, 3)
        layout2.addWidget(QWidget(), 0, 4)
        layout2.setColumnStretch(4, 1)
        wdg = QWidget()
        wdg.setLayout(layout2)
        layout.addWidget(wdg, 3, 0)

        layout.addWidget(QLabel("Speed:"), 4, 0)
        spinbox_speed = QSpinBox()
        spinbox_speed.setMinimum(0)
        spinbox_speed.setMaximum(100)
        spinbox_speed.setSingleStep(10)
        spinbox_speed.setValue(50)
        layout.addWidget(spinbox_speed, 5, 0)

        # Just to fill the space
        layout.addWidget(QWidget(), 100, 0)
        layout.setRowStretch(100, 1)

        return right_widget

    def _get_left_widget(self, view) -> QWidget:
        left_widget = QWidget()
        left_widget.setAutoFillBackground(True)
        palette = left_widget.palette()
        palette.setColor(QPalette.Window, Qt.GlobalColor.green)
        left_widget.setPalette(palette)

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
