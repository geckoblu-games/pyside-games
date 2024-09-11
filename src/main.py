#!/usr/bin/python3
import argparse
import sys

from PySide6.QtGui import QIcon, QScreen
from PySide6.QtWidgets import QVBoxLayout, QApplication, QPushButton, QDialog

import snake
import sokoban.main
import mazegenerator.main


class MainWindow(QDialog):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("PySide6 Games")
        self.setWindowIcon(QIcon(':/qt-project.org/logos/pysidelogo.png'))

        self.game = None

        self.layout = QVBoxLayout()

        # pylint: disable=no-member
        button = QPushButton("Snake")
        button.clicked.connect(lambda: self.the_button_was_clicked('snake'))
        self.layout.addWidget(button)

        button = QPushButton("Sokoban")
        button.clicked.connect(lambda: self.the_button_was_clicked('sokoban'))
        self.layout.addWidget(button)

        button = QPushButton("Maze Generator")
        button.clicked.connect(lambda: self.the_button_was_clicked('mazegenerator'))
        self.layout.addWidget(button)

        self.setLayout(self.layout)

        # widget = QWidget()
        # widget.setLayout(layout)
        # self.setCentralWidget(widget)

    def the_button_was_clicked(self, game):
        print("Clicked!", game)
        self.game = game
        self.accept()


def main():

    app = None

    # if no game is passed by the command line, show a dialog
    if args.game is None:
        app = QApplication(sys.argv)

        window = MainWindow()
        window.show()
        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = window.frameGeometry()
        geo.moveCenter(center)
        window.move(geo.topLeft())

        if window.exec():
            args.game = window.game

    if args.game == 'snake':
        snake.main(app)
    elif args.game == 'sokoban':
        sokoban.main.main(app)
    elif args.game == 'mazegenerator':
        mazegenerator.main.main(app)


def parse_cmdline():
    parser = argparse.ArgumentParser()

    parser.add_argument('--game', choices=['snake', 'sokoban', 'mazegenerator'],
                        type=str.lower, help='directly starts the provided game')

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_cmdline()  # pylint: disable=invalid-name
    # print(args)

    sys.exit(main())
