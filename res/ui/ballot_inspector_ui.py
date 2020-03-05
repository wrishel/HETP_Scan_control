# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ballot_inspector_ui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_BallotInspector(object):
    def setupUi(self, BallotInspector):
        BallotInspector.setObjectName("BallotInspector")
        BallotInspector.resize(827, 633)
        BallotInspector.setStyleSheet("background-color: rgb(220, 255, 255);")
        self.horizontalLayout = QtWidgets.QHBoxLayout(BallotInspector)
        self.horizontalLayout.setContentsMargins(9, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.zoomOutPB = QtWidgets.QPushButton(BallotInspector)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.zoomOutPB.setFont(font)
        self.zoomOutPB.setStyleSheet("background-color: rgb(245, 243, 246);")
        self.zoomOutPB.setObjectName("zoomOutPB")
        self.verticalLayout_2.addWidget(self.zoomOutPB)
        self.zoomInPB = QtWidgets.QPushButton(BallotInspector)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.zoomInPB.setFont(font)
        self.zoomInPB.setStyleSheet("background-color: rgb(245, 243, 246);")
        self.zoomInPB.setObjectName("zoomInPB")
        self.verticalLayout_2.addWidget(self.zoomInPB)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.otherSidePB = QtWidgets.QPushButton(BallotInspector)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.otherSidePB.setFont(font)
        self.otherSidePB.setStyleSheet("background-color: rgb(245, 243, 246);")
        self.otherSidePB.setObjectName("otherSidePB")
        self.verticalLayout_2.addWidget(self.otherSidePB)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem4)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem5)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem6)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem7)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem8)
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem9)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.addImageViewerHere = QtWidgets.QHBoxLayout()
        self.addImageViewerHere.setContentsMargins(1, 1, 1, 1)
        self.addImageViewerHere.setObjectName("addImageViewerHere")
        self.horizontalLayout.addLayout(self.addImageViewerHere)

        self.retranslateUi(BallotInspector)
        QtCore.QMetaObject.connectSlotsByName(BallotInspector)

    def retranslateUi(self, BallotInspector):
        _translate = QtCore.QCoreApplication.translate
        BallotInspector.setWindowTitle(_translate("BallotInspector", "Form"))
        self.zoomOutPB.setText(_translate("BallotInspector", "Zoom Out"))
        self.zoomInPB.setText(_translate("BallotInspector", "Zoom In"))
        self.otherSidePB.setText(_translate("BallotInspector", "Other Side"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    BallotInspector = QtWidgets.QWidget()
    ui = Ui_BallotInspector()
    ui.setupUi(BallotInspector)
    BallotInspector.show()
    sys.exit(app.exec_())
