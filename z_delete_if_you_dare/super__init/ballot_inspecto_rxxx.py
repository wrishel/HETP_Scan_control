
from QtImageViewer_xxx import QtImageViewer
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from res.ui.ballot_inspector_ui import Ui_BallotInspector


class Ballot_inspector(QtImageViewer):
    def __init__(self):
        super().__init__()
        #dpm - instantiate the main window as python object but not yet hooked to Qt
        self.main_ui = Ui_BallotInspector()
        self.main_ui.setupUi(self)
        self.main_ui.addImageViewerHere.addWidget(QtImageViewer())

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ballot_inspector = Ballot_inspector()
    window = ballot_inspector
    window.show()


    print(f"app exits with value: {app.exec_()}", file=sys.stderr)
