
'''Scanning step 3 for recovering from a batch where there were no good images scanned.

   Depending on the work flow this could be the third step or it might be the second.'''

# todo: Give different instructions for a one-sided ballot to simplify the two-sided.
# todo: Use QWebEngineView to get <DIV> to work in the HTML, see https://doc.qt.io/qtforpython/PySide2/QtWebEngineWidgets/QWebEngineView.html

from ballot_inspector import Ballot_inspector
from etpconfig import Scanconfig
from scanner_hardware import Batch_status
import GLB_globals
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication, QPoint
from PyQt5.QtWidgets import QWidget, QApplication
import sys


GLB = GLB_globals.get()

# todo: if time: Designer changes to make the three entry boxes the same size and smaller.

class ScanError3(QWidget):
    """Panel for recovery from scanner error on first sheet in batch."""

    def __init__(self, exit_app, uicpath, main_panel_widget):
        super().__init__()
        uic.loadUi(uicpath, self)
        self.exit_app = exit_app
        self.doublesided = GLB.config['ballot']['doublesided']
        self.main_panel_widget = main_panel_widget
        self.inspector_window = Ballot_inspector()
        self.cancelPB.pressed.connect(self.cancelPB_pressed)
        self.rescanPB.pressed.connect(self.rescanPB_pressed)


    def invoke(self, front_page, back_page):
        # position the my window on the left and the inspector on the right
        #
        self.inspector_window.show()
        self.inspector_window.raise_()
        app = QApplication.instance()
        desktop = app.desktop()
        avail_geom = desktop.availableGeometry()
        avail_width = avail_geom.width()
        my_size = self.main_panel_widget.size()
        inspector_width = self.inspector_window.size().width()
        # print(f'avaailable ={avail_width}, mysize=={my_size}, inspect width={inspector_width}')
        horiz_space_avail = int((avail_width - (my_size.width() + inspector_width)))
        if horiz_space_avail <= 0:
            my_left = 0
            inspector_left = avail_width - inspector_width
        else:
            my_left = horiz_space_avail/3
            inspector_left = avail_width - (horiz_space_avail/3 + inspector_width)

        GLB.main_window.move(my_left, 100)
        self.inspector_window.move(inspector_left, 100)
        self.inspector_window.set_ballot_pair(front_page, back_page)
        self.inspector_window.show()

    # signal handling methods

    def rescanPB_pressed(self):
        """Begin rescanning the batch from the start."""

        bsb = GLB.batch_status
        GLB.batch_status.restart_batch_params()
        GLB.transitioner.set_current_panel('scanning')
        self.inspector_window.hide()
        return

    def cancelPB_pressed(self):
        bsb = GLB.batch_status
        GLB.transitioner.set_current_panel('scan_pre')

    # ---------------------------  entry_check  ---------------------------

    def entry_check(self):
        """Called from transitioner before switching to this screen."""

        # initialize the UI
        #
        bsb = GLB.batch_status
        self.next_seq_num = bsb.next_seq_num_in_batch - bsb.sided
        self.invoke(bsb.front_path, bsb.back_path)
        return True

    # validity checking before exiting the panel

    def exit_check(self, departureType='continue'):
        """Test for consistency among Admin settings. Return True if the operation should continue.
           e.g., no error or user response was "ignore"."""

        return True


if __name__== '__main__':
    # informal list of things to test
    #
    #   todo: Elections Batch number has been seen before.
    #   todo: sequence number already exists

    from PyQt5.QtCore import QTimer
    from transitioner import Transitioner_for_testing

    app = QApplication(sys.argv)
    GLB = GLB_globals.get()
    GLB.transitioner = Transitioner_for_testing()
    GLB.transitioner.add_widget_main_panels(ScanError3(QCoreApplication.quit,
                                        "res/ui/scan_error_2.ui", GLB.transitioner.main_panel_stack),
                                        'scan_error3')
    GLB.transitioner.set_current_panel('scan_error3')
    window = GLB.transitioner.main_panel_stack
    window.show()
    app.exec_()

