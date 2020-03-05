# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'z_extwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(408, 804)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.viewerVerticalLayout = QtWidgets.QVBoxLayout()
        self.viewerVerticalLayout.setContentsMargins(-1, -1, -1, 8)
        self.viewerVerticalLayout.setObjectName("viewerVerticalLayout")
        self.graphicsView = QtWidgets.QGraphicsView(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(200)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName("graphicsView")
        self.viewerVerticalLayout.addWidget(self.graphicsView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.otherSidePB = QtWidgets.QPushButton(Form)
        self.otherSidePB.setStyleSheet("background-color: rgb(232, 232, 232);")
        self.otherSidePB.setObjectName("otherSidePB")
        self.horizontalLayout.addWidget(self.otherSidePB)
        self.resetPB = QtWidgets.QPushButton(Form)
        self.resetPB.setStyleSheet("background-color: rgb(232, 232, 232);")
        self.resetPB.setObjectName("resetPB")
        self.horizontalLayout.addWidget(self.resetPB)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.viewerVerticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.viewerVerticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.otherSidePB.setText(_translate("Form", "Other side"))
        self.resetPB.setText(_translate("Form", "Reset "))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
