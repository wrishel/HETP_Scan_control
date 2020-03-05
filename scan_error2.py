
'''Scanning step 2 of recovering from a scanner error stoop
'''

# todo: future: Give different instructions for a one-sided ballot to simplify the two-sided.
# todo: future: Use QWebEngineView to get <DIV> to work in the HTML, see https://doc.qt.io/qtforpython/PySide2/QtWebEngineWidgets/QWebEngineView.html

from ballot_inspector import Ballot_inspector
from ETP_util import fullpath_to_image
from etpconfig import Scanconfig
from scanner_hardware import Batch_status
import GLB_globals
import os
from os.path import isfile
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication, QPoint
from PyQt5.QtWidgets import QWidget, QApplication
import sys

GLB = GLB_globals.get()

class ScanError2(QWidget):
    """Panel for after a batch has finished successfully"""

    def __init__(self, exit_app, uicpath, main_panel_widget):
        super().__init__()
        uic.loadUi(uicpath, self)
        self.exit_app = exit_app
        self.doublesided = GLB.config['ballot']['doublesided']
        self.main_panel_widget = main_panel_widget
        self.inspector_window = Ballot_inspector()
        self.resumePB.pressed.connect(self.resumePB_pressed)
        self.back1PB.pressed.connect(self.back1PB_pressed)
        self.forward1PB.pressed.connect(self.forward1PB_pressed)
        # self.dbg_putative = 2             # set 0 when not debugging
                                            # todo: polishing: set all debug parameters in systematic way
        self.initial_front_path = None
        self.alternate_image = GLB.ROOT_DIR + 'res/img/img_not_available.jpg'
        self.initial_next_seq_num = None     # save this to find what to delete when resuming scanning

    def invoke(self, front_page, back_page):
        """Open the ballot inspector."""

        front_page = self.possible_sub(front_page)
        back_page = self.possible_sub(back_page)
        app = QApplication.instance()
        desktop = app.desktop()
        avail_geom = desktop.availableGeometry()
        avail_width = avail_geom.width()
        my_size = self.main_panel_widget.size()
        inspector_width = self.inspector_window.size().width()
        horiz_space_avail = int((avail_width - (my_size.width() + inspector_width)))
        if horiz_space_avail <= 0:
            my_left = 0
            inspector_left = avail_width - inspector_width
        else:
            my_left = horiz_space_avail/3
            inspector_left = avail_width - (horiz_space_avail/3 + inspector_width)

        self.ui_set_consistency()
        # todo: if time: expand the inspector window vertically to operate the screen.

        if GLB.main_window is not None:         # skip this for testing in __main__
            GLB.main_window.move(my_left, 100)
        self.inspector_window.move(inspector_left, 100)
        self.inspector_window.set_ballot_pair(front_page, back_page)
        self.inspector_window.show()
        self.inspector_window.raise_()

    def possible_sub(self, putative_file) -> str:
        """
        If there is no image at putative_file, return the path of a special imaage.

        putative_file: path"""

        if isfile(putative_file):
            return putative_file
        else:
            return GLB.ROOT_DIR + 'res/img/img_not_available.jpg'

    # signal handling methods

    def back1PB_pressed(self):
        """Back up the batch status one sheet so that the next time the inspector is invoked it
           shows the prior images.

           Later at the end of scan_error2, delete any images from the database that have been
           backed over. The delayed deletion allows for moving forward again."""

        bsb = GLB.batch_status
        bsb.dbg_conditional_trace(False, 'before backing up one sheet')
        if bsb.back_up_one_sheet():
            self.invoke(bsb.front_path, bsb.back_path)
            bsb.dbg_conditional_trace(False, 'after backing up one sheet')
            self.ui_set_consistency()
            return

        else:
            # couldn't back up because already at the front of the batch
            self.ui_set_consistency()
            return

    def forward1PB_pressed(self):
        """Move the images being viewed forward one sheet"""

        bsb = GLB.batch_status
        if bsb.forward_one_sheet():
            self.invoke(bsb.front_path, bsb.back_path)

        bsb.dbg_conditional_trace(False, 'after moving forward one sheet')
        self.ui_set_consistency()

    def resumePB_pressed(self):
        self.inspector_window.hide()
        GLB.transitioner.set_current_panel('scanning')

    # -------------------------  UI Consistency  --------------------------

    def ui_set_consistency(self):
        """Set the state of various UI widgets to match the current data"""

        bsb = GLB.batch_status
        if bsb.OK_to_backup():
            self.back1PB.setEnabled(False)
        else:
            self.back1PB.setEnabled(True)

        if self.initial_front_path and bsb.front_path < self.initial_front_path:
            self.forward1PB.setEnabled(True)
        else:
            self.forward1PB.setEnabled(False)

    # ---------------------------  entry check  ---------------------------

    def entry_check(self):
        """Called from transitioner before switching to this screen."""

        bsb = GLB.batch_status
        self.initial_next_seq_num = bsb.next_seq_num_in_batch
        self.initial_front_path = bsb.front_path
        self.ui_set_consistency()
        front = self.possible_sub(bsb.front_path)
        back = self.possible_sub(bsb.back_path)
        self.invoke(front, back)
        return True

    # ---------------------------  exit check  ---------------------------

    def exit_check(self, departureType='continue'):
        """Test for consistency among Admin settings. Return True if the operation should continue.
           e.g., no error or user response was "ignore"."""

        bsb = GLB.batch_status
        simulating = GLB.config['Scanning']['simulating']
        self.initial_front_path = None
        if self.initial_next_seq_num > bsb.next_seq_num_in_batch:
            deletions = range(bsb.next_seq_num_in_batch,
                              self.initial_next_seq_num)


            if not simulating:
                assert False, "How to test this?"
                for filenum in deletions:
                    f = fullpath_to_image(filenum)
                    if isfile(f):

                        os.remove(f)
                        print(f'deleting file: {f}', file = sys.stderr)

                    else:
                        print(f'not a file: {f}', file = sys.stderr)

            GLB.db.delete_images(deletions)
        return True


if __name__== '__main__':
    # informal list of things to test
    #
    #   operatorLE gets new vs previously used initials
    #   Elections batch number is odd on double-sided ballot
    #   todo: sequence number already exists
    #   todo: new operator id gets entered in config
    #   todo: in scanning.py elections batch number is entered in config

    from PyQt5.QtCore import QTimer
    from transitioner import Transitioner_for_testing

    app = QApplication(sys.argv)
    GLB = GLB_globals.get()
    GLB.transitioner = Transitioner_for_testing()
    GLB.transitioner.add_widget_main_panels(ScanError2(QCoreApplication.quit,
                                        "res/ui/scan_error_2.ui", GLB.transitioner.main_panel_stack),
                                        'scan_error2')
    GLB.transitioner.set_current_panel('scan_error2')
    window = GLB.transitioner.main_panel_stack
    window.show()
    app.exec_()

