"""sinple use of args"""

# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

In this example, we show how to
emit a custom signal.

Author: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""

import sys
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QApplication


class Communicate(QObject):
    print('create signal')
    closeAppSig = pyqtSignal(str)


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.c = Communicate()
        self.c.closeAppSig.connect(self.gotcha)

    def initUI(self):
        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Emit signal')
        print('app shown')
        self.show()

    def mousePressEvent(self, event):       # reimplented from QMainWindow
        print('mouse pressed')
        self.c.closeAppSig.emit('abc')

    def gotcha(self, s):
        print(s)
        self.close()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    app.exec_()
    print('app exited')
    sys.exit()