# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_a.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!
import sys

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_widgetA(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

    def setupUi(self):
        self.setObjectName("widgetA")
        self.resize(198, 144)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel()
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.pushButton = QtWidgets.QPushButton()
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

app = QtWidgets.QApplication(sys.argv)
w = Ui_widgetA()
w.setupUi()
w.show()
exec(app.exec())