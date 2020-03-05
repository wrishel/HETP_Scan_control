# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_a.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_widgetA(object):
    def setupUi(self, widgetA):
        widgetA.setObjectName("widgetA")
        widgetA.resize(198, 144)
        self.verticalLayout = QtWidgets.QVBoxLayout(widgetA)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(widgetA)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.pushButton = QtWidgets.QPushButton(widgetA)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(widgetA)
        QtCore.QMetaObject.connectSlotsByName(widgetA)

    def retranslateUi(self, widgetA):
        _translate = QtCore.QCoreApplication.translate
        widgetA.setWindowTitle(_translate("widgetA", "Form"))
        self.label.setText(_translate("widgetA", "This is A"))
        self.pushButton.setText(_translate("widgetA", "Switch to B"))
