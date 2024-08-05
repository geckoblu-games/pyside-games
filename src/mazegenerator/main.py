import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from mazegenerator.mainwindow import MainWindow


def main(app=None):

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # QApplication.setWindowIcon(QIcon(":/images/icon.svg"))
    QApplication.setApplicationName("MazeGenerator")
    QApplication.setOrganizationDomain("geckoblu.net")
    QApplication.setOrganizationName("geckoblu")

    if not app:
        app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == '__main__':
    main()