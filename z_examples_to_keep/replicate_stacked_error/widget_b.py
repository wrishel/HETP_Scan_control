# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_b.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_widgetB(object):
    def setupUi(self, widgetB):
        widgetB.setObjectName("widgetB")
        widgetB.resize(197, 144)
        self.verticalLayout = QtWidgets.QVBoxLayout(widgetB)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(widgetB)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.pushButton = QtWidgets.QPushButton(widgetB)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(widgetB)
        QtCore.QMetaObject.connectSlotsByName(widgetB)

    def retranslateUi(self, widgetB):
        _translate = QtCore.QCoreApplication.translate
        widgetB.setWindowTitle(_translate("widgetB", "Form"))
        self.label.setText(_translate("widgetB", "This is B"))
        self.pushButton.setText(_translate("widgetB", "Switch to A"))
