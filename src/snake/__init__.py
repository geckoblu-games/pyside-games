import sys

from PySide6.QtWidgets import QApplication

from snake.main import MainWindow


def main(app=None):
    if not app:
        app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == '__main__':
    main()
