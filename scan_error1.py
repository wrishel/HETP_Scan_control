
'''Scanning error: Step 1 in the recover from a scanner error.
'''

import GLB_globals
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget, QApplication
import sys

# todo: polishing -- screen is uncentered, probably because the stack_widget is uncentered.

GLB = GLB_globals.get()

# todo: if time: Designer changes to make the three entry boxes the same size and smaller.

class ScanError1(QWidget):
    """Panel for after a batch has finished successfully"""

    def __init__(self, exit_app, uicpath):
        super().__init__()
        self._ui(uicpath)
        self.exit_app = exit_app

        # set signal connections AFTER initial values loaded
        self.nextStepPB.clicked.connect(self.nextStepPB_pressed)

    def _ui(self, uicpath):
        uic.loadUi(uicpath, self)

    # signal handling methods

    def nextStepPB_pressed(self):
        GLB.transitioner.set_current_panel('scan_error2')

    # ---------------------------  entry_check  ---------------------------

    def entry_check(self):
        """Called from transitioner before switching to this screen.

           Return is a bool indicating whether it is OK to enter,
           WHICH MUST BE TRUE IN EVERY SCENARIO BECAUSE THE PREVIOUS PANEL
           WAS THE SCANNER RUNNING."""

        return True

    # validity checking before exiting the panel

    def exit_check(self, departureType='continue'):
        """Test for consistency among Admin settings. Return True if the operation should continue.
           e.g., no error or user response was "ignore"."""

        return True


if __name__== '__main__':

    from PyQt5.QtCore import QTimer
    from transitioner import Transitioner_for_testing

    app = QApplication(sys.argv)
    GLB = GLB_globals.get().set_object_instances()
    GLB.transitioner = Transitioner_for_testing()
    GLB.transitioner.add_widget_main_panels(ScanError1(QCoreApplication.quit,
                                                 "res/ui/scan_error.ui"),
                                        'scan_error_1')
    GLB.transitioner.set_current_panel('scan_error_1')
    window = GLB.transitioner.main_panel_stack
    window.show()
    app.exec_()

