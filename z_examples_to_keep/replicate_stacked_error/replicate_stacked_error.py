"""This shows a correct implementation of switching widgets"""

import sys
from PyQt5 import QtWidgets, QtCore, QtGui, uic

class MainWindow(QtWidgets.QWidget):
    def __init__(self, widga, widgb):
        super().__init__()
        uic.loadUi('mainwindow.ui', self)
        self.addWidget(widga)
        self.addWidget((widgb))

    def addWidget(self, widget):
        self.stackedWidget.addWidget(widget)

    def switchToWidget(self, letter):
        num = ord(letter) - ord('A')
        self.stackedWidget.setCurrentIndex(num)


class Ui_widgetAorB(QtWidgets.QWidget):
    def __init__(self, AorB):
        super().__init__()
        self.mainwindow = None      # added by caller
        self.AorB = AorB
        self.BorA = "B" if AorB == "A" else "A"
        self.setObjectName(f"Widget{AorB}")
        self.resize(198, 144)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(self)
        self.label.setText(f"This is {AorB}")
        self.verticalLayout.addWidget(self.label)
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setText(f"Goto {self.BorA}")
        self.verticalLayout.addWidget(self.pushButton)
        self.pushButton.clicked.connect(self.handle_click)

    def handle_click(self):
        self.mainwindow.switchToWidget(self.BorA)


app = QtWidgets.QApplication(sys.argv)
widga = Ui_widgetAorB('A')
widgb = Ui_widgetAorB('B')
main_window = MainWindow(widga, widgb)
widga.mainwindow = main_window
widgb.mainwindow = main_window
main_window.show()
sys.exit(app.exec())
