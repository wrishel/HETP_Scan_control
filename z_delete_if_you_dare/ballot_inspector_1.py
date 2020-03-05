# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ballot_inspector_1.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_BallotInspector(object):
    def setupUi(self, BallotInspector):
        BallotInspector.setObjectName("BallotInspector")
        BallotInspector.resize(827, 633)
        self.verticalLayout = QtWidgets.QVBoxLayout(BallotInspector)
        self.verticalLayout.setObjectName("verticalLayout")
        self.hl4 = QtWidgets.QHBoxLayout()
        self.hl4.setObjectName("hl4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hl4.addItem(spacerItem)
        self.otherSidePB = QtWidgets.QPushButton(BallotInspector)
        self.otherSidePB.setObjectName("otherSidePB")
        self.hl4.addWidget(self.otherSidePB)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hl4.addItem(spacerItem1)
        self.zoomInPB = QtWidgets.QPushButton(BallotInspector)
        self.zoomInPB.setObjectName("zoomInPB")
        self.hl4.addWidget(self.zoomInPB)
        self.zoomOutPB = QtWidgets.QPushButton(BallotInspector)
        self.zoomOutPB.setObjectName("zoomOutPB")
        self.hl4.addWidget(self.zoomOutPB)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hl4.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.hl4)
        self.addImageViewerHere = QtWidgets.QHBoxLayout()
        self.addImageViewerHere.setObjectName("addImageViewerHere")
        self.verticalLayout.addLayout(self.addImageViewerHere)

        self.retranslateUi(BallotInspector)
        QtCore.QMetaObject.connectSlotsByName(BallotInspector)

    def retranslateUi(self, BallotInspector):
        _translate = QtCore.QCoreApplication.translate
        BallotInspector.setWindowTitle(_translate("BallotInspector", "Form"))
        self.otherSidePB.setText(_translate("BallotInspector", "Other Side"))
        self.zoomInPB.setText(_translate("BallotInspector", "Zoom In"))
        self.zoomOutPB.setText(_translate("BallotInspector", "Zoom Out"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    BallotInspector = QtWidgets.QWidget()
    ui = Ui_BallotInspector()
    ui.setupUi(BallotInspector)
    BallotInspector.show()
    sys.exit(app.exec_())
