

'''Ballot Inspector, a free-standing window for inspecting a ballot.

   Unlike other GUI objects this does not operate as a panel within HETP_main and
   is not invoked through transitioner.py.

'''

# todo: make window aspect ratio proportional to aspect ratio of ballot + buttons

from collections import deque
from QtImageViewer_wes import QtImageViewer
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from res.ui.ballot_inspector_ui import Ui_BallotInspector
import sys

import GLB_globals
GLB = GLB_globals.get()

class Ballot_inspector(QtImageViewer):
    """Free-standing window for examining a ballot -- front and back sides."""

    def __init__(self):
        super().__init__()

        # main windows designed in Designer as res/ui/ballot_inspector_ui.ui then
        # converted to Python code in Ui_BallotInspector.py
        # instantiate the main window as python object but not yet hooked to Qt
        self.main_ui = Ui_BallotInspector()
        self.main_ui.setupUi(self)
        self.qtiv = QtImageViewer()      # local handle to image viewer
        self.main_ui.addImageViewerHere.addWidget(self.qtiv)
        self.qtiv.canZoom = True
        self.qtiv.canPan = True
        self.qtiv.setStyleSheet('background-color: rgb(245, 245, 245);')
        # self.set_ballot_pair(front_page, back_page)

        # connect signals
        #
        self.main_ui.zoomInPB.clicked.connect(self.respond_to_zoom_in_button)
        self.main_ui.zoomOutPB.clicked.connect(self.respond_to_zoom_out_button)
        self.main_ui.otherSidePB.clicked.connect(self.respond_to_other_side_button)
        # self.main_ui.closePB.clicked.connect(self.close)

    def set_ballot_pair(self, front, back=None):
        """A ballot is potentially a pair of images, front and back of the sheet.

           If this ballot is single-sided then back should be None.
        """

        self.sides = deque([front, back])
        self.qtiv.zoom_all_out()
        GLB.signals.inspector_viewing.emit(self.sides[0])
        self.qtiv.loadImageFromFile(self.sides[0])

    def respond_to_zoom_in_button(self):
        self.qtiv.zoom_in_out(1, 0.20)

    def respond_to_zoom_out_button(self):
        self.qtiv.zoom_in_out(-1, 0.25)

    def respond_to_other_side_button(self):
        if self.sides[1] is not None:
            self.sides.extendleft((self.sides.pop(),))
            self.qtiv.loadImageFromFile(self.sides[0])
            GLB.signals.inspector_viewing.emit(self.sides[0])
            # self.qtiv.zoom_all_out()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ballot_inspector = Ballot_inspector('test_data/000000.jpg', 'test_data/000001.jpg'())
    window = ballot_inspector
    window.show()
    print(f"app exits with value: {app.exec_()}", file=sys.stderr)
