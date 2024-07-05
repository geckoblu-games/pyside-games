from PySide6.QtWidgets import QDialog, QDialogButtonBox, QComboBox, QVBoxLayout, \
    QLabel

from sokoban.levels import get_sets, get_levels_count

class ChooseLevelDialog(QDialog):

    def __init__(self, parent, current_set, current_level):
        super().__init__(parent)

        self.setWindowTitle("Choose a level")

        buttons = QDialogButtonBox.Ok

        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)  # pylint: disable=no-member
        self.button_box.rejected.connect(self.reject)  # pylint: disable=no-member

        self.sets_combo = QComboBox()
        self.sets_combo.addItems(get_sets())
        self.sets_combo.setCurrentText(current_set)
        self.sets_combo.currentTextChanged.connect(self._set_changed)  # pylint: disable=no-member

        self.levels_combo = QComboBox()
        levels = [str(level) for level in range(1, get_levels_count(current_set) + 1)]
        self.levels_combo.addItems(levels)
        self.levels_combo.setCurrentIndex(current_level)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.sets_combo)
        self.layout.addWidget(self.levels_combo)
        self.layout.addWidget(QLabel(" "))
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def _set_changed(self, setname: str):
        levels = [str(level) for level in range(1, get_levels_count(setname) + 1)]
        self.levels_combo.clear()
        self.levels_combo.addItems(levels)

    def get_choice(self):
        return (self.sets_combo.currentText(), self.levels_combo.currentIndex())
