import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import mazegenerator.resources  # pylint: disable=unused-import
from mazegenerator.mainwindow import MainWindow


def main(app=None):

    QApplication.setWindowIcon(QIcon(":/images/icon.svg"))
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
