
'''Scanning panel: Mainpanals page after a batch has ended normally.
'''
from etpconfig import Scanconfig
import GLB_globals
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget, QApplication
import sys

# todo: polishing -- screen is uncentered, probably because the stack_widget is uncentered.

# GLB = None       # magically gets redefined through GLB_globals
GLB = GLB_globals.get()

# todo: if time: Designer changes to make the three entry boxes the same size and smaller.

class ScanPost(QWidget):
    """Panel for after a batch has finished successfully"""

    def __init__(self, exit_app, uicpath):
        super().__init__()
        self._ui(uicpath)
        self.exit_app = exit_app
        self.doublesided = GLB.config['ballot']['doublesided']

        # set signal connections AFTER initial values loaded
        self.quitPB.clicked.connect(exit_app)  # todo: Jump to close-app screen
        self.newBatchPB.clicked.connect(self.newBatchPB_pressed)

    def _ui(self, uicpath):
        uic.loadUi(uicpath, self)

    def report(self, batch_status):
        """Produce text lines that describe the batch just completed."""

        bsb = GLB.batch_status
        s = f"Batch start time: {bsb.batch_start_time}\n"
        s += f"Images scanned: {bsb.images_scanned}\n"
        s += f"Sequence numbers: {bsb.first_seq_num_in_batch} - " \
             f"{bsb.next_seq_num_in_batch - 1}\n"
        s += f"Operator: {bsb.operator_id}\n"
        s += f"Elections batch number: {bsb.elections_batch_num}\n"
        print(s)
        return s

    # signal handling methods

    def newBatchPB_pressed(self):
        GLB.transitioner.set_current_panel('scan_pre')

    # ---------------------------  entry_check  ---------------------------

    def entry_check(self):
        """Called from transitioner before switching to this screen.

           Return is a bool indicating  whether it is OK to enter,
           WHICH MUST BE TRUE IN EVERY SCENARIO BECAUSE THE PREVIOUS PANEL
           WAS THE SCANNER RUNNING."""

        # todo: the following should generalized as a method in etpconfig.py
        election_batch = GLB.batch_status.elections_batch_num
        election_batch_list = GLB.config['Scanning']['electionsbatches']\
                .replace(' ', '').split('|')
        if election_batch not in election_batch_list:
            election_batch_list.append(election_batch)
            GLB.config['Scanning']['electionsbatches'] = '|'.join(election_batch_list)

        GLB.config.write()

        # initialize the UI
        #
        self.batchresultsBRWS.setPlainText(self.report(GLB.batch_status))
        return True

    # validity checking before exiting the panel

    def exit_check(self, departureType='continue'):
        """Test for consistency among Admin settings. Return True if the operation should continue.
           e.g., no error or user response was "ignore"."""

        # todo: Add this elections batch num to accumulated electionsbatches.
        return True


if __name__== '__main__':
    # informal list of things to test
    #
    #   operatorLE gets new vs previously used initials
    #   todo: Elections Batch number has been seen before.
    #   Elections batch number is odd on double-sided ballot
    #   todo: sequence number already exists
    #   todo: new operator id gets entered in config
    #   todo: in scanning.py elections batch number is entered in config

    from PyQt5.QtCore import QTimer
    from transitioner import Transitioner_for_testing

    app = QApplication(sys.argv)
    GLB = GLB_globals.get().set_object_instances()
    GLB.transitioner = Transitioner_for_testing()
    # transitioner = Transitioner_for_testing()
    # config = Scanconfig('etp.ini')
    GLB.transitioner.add_widget_main_panels(ScanPost(QCoreApplication.quit,
                                                 "res/ui/scan_post.ui"),
                                        'scan_post')
    GLB.transitioner.set_current_panel('scan_post')
    window = GLB.transitioner.main_panel_stack
    window.show()
    app.exec_()

