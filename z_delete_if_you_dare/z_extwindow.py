
from PyQt5 import QtCore, QtGui, QtWidgets
from zoom import QtImageViewer

class Ui_Form(QtWidgets.QWidget):
    """An independent window to show the front and back of a ballot, allowing zooming.

       This is based on QtImageViewer https://github.com/marcel-goldschen-ohm/PyQtImageViewer/blob/master/QtImageViewer.py
    """

    def __init__(self, front, back):
        super().__init__()
        self.sides = [front, back]
        self.setupUi()

    def setupUi(self):
        Form.setObjectName("Form")
        Form.resize(408, 804)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.viewerVerticalLayout = QtWidgets.QVBoxLayout()
        self.viewerVerticalLayout.setObjectName("viewerVerticalLayout")
        self.graphicsView = QtImageViewer()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(200)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.loadImageFromFile(self.sides[0])
        # self.graphicsView = QtWidgets.QGraphicsView(self.layoutWidget)
        self.graphicsView.setObjectName("graphicsView")
        self.viewerVerticalLayout.addWidget(self.graphicsView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.otherSidePB = QtWidgets.QPushButton(Form)
        self.otherSidePB.setStyleSheet("background-color: rgb(232, 232, 232);")
        self.otherSidePB.setObjectName("otherSidePB")
        self.otherSidePB.setText("Other side")
        self.horizontalLayout.addWidget(self.otherSidePB)
        self.resetPB = QtWidgets.QPushButton(Form)
        self.resetPB.setStyleSheet("background-color: rgb(232, 232, 232);")
        self.resetPB.setObjectName("resetPB")
        self.resetPB.setText("Reset")
        self.horizontalLayout.addWidget(self.resetPB)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.viewerVerticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.viewerVerticalLayout)
        self.otherSidePB.pressed.connect(self.other_side)
        self.resetPB.pressed.connect(self.reset)


    def other_side(self):
        self.graphicsView.loadImageFromFile(self.switch_sides())
        print('other side')

    def reset(self):
        self.graphicsView.ext_resetzoom('ext')
        print('reset')

    def current_side(self):
        return self.sides[0]

    def switch_sides(self):
        self.sides.reverse()
        return self.sides[0]

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form("/Users/Wes/Dropbox/Programming/ElectionTransparency/NewUI/NewUI_stacked/test_data/000000.jpg",
                 "/Users/Wes/Dropbox/Programming/ElectionTransparency/NewUI/NewUI_stacked/test_data/000001.jpg")

    Form.show()
    sys.exit(app.exec_())
