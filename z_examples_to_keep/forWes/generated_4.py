# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_generated_4.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(898, 720)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.zoomIn = QtWidgets.QPushButton(self.centralwidget)
        self.zoomIn.setEnabled(True)
        self.zoomIn.setObjectName("zoomIn")
        self.horizontalLayout_3.addWidget(self.zoomIn)
        self.zoomOut = QtWidgets.QPushButton(self.centralwidget)
        self.zoomOut.setEnabled(True)
        self.zoomOut.setObjectName("zoomOut")
        self.horizontalLayout_3.addWidget(self.zoomOut)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.hlImage = QtWidgets.QHBoxLayout()
        self.hlImage.setObjectName("hlImage")
        self.verticalLayout_2.addLayout(self.hlImage)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Ballot Inspector"))
        self.zoomIn.setText(_translate("MainWindow", "Zoom In"))
        self.zoomOut.setText(_translate("MainWindow", "Zoom Out"))
