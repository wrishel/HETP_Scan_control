
'''Scanning panel: Main panal shown while the scanner is running.
'''
import copy
from etpconfig import Scanconfig
import GLB_globals
from scanner_hardware import Batch_status  # access through GLB
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QWidget, QApplication
import sys

GLB = GLB_globals.get()

# todo: polishing: if time Designer changes to make the three entry boxes the same size and narrow.

class Scanning(QWidget):
    """Pre-scan panel"""

    def __init__(self, exit_app, uicpath):
        super().__init__()
        self._ui(uicpath)
        self.exit_app = exit_app
        GLB.signals.scan_complete.connect(self.complete)
        GLB.signals.scan_error.connect(self.gave_up_on_error)
        GLB.signals.scan_update.connect(self.scanner_upate)
        # NOT HERE

    def _ui(self, uicpath):
        uic.loadUi(uicpath, self)

    # signal handling methods -- running in different threads than scanning.py

    def complete(self):
        """Handle the scanner finishing with no unrecovered errors"""
        GLB.transitioner.set_current_panel('scan_post')

    def scanner_upate(self):
        """Handle interim progress reports from scanner"""
        bsb = GLB.batch_status
        # print(f"{bsb.front_path}, {bsb.back_path}", file=sys.stderr)
        self.next_seq_numSB.setValue(bsb.next_seq_num_in_batch)


    def gave_up_on_error(self):
        """Scanner signaled an error"""

        GLB.transitioner.set_current_panel('scan_error1')
    # ----------------------  entry_check  ----------------------

    def entry_check(self):
        """Called from transitioner before switching to this screen. Return is a bool indicating
           whether it is OK to enter."""

        # populate the screen
        #
        self.opid = GLB.config['Scanning']['operatorid']
        assert bool(self.opid), "No operator ID"
        self.operatorLE.setText(self.opid)
        bsb = GLB.batch_status
        self.elections_batch_numLE.setText(str(bsb.elections_batch_num))
        # self.next_seq_numSB.setValue(int(GLB.batch_status.next_seq_num_in_batch)) getting None

        if not bsb.is_stopped_on_error():
            bsb.images_scanned = 0

            # get next seq number from DB when simulating and from file system when live
            # todo: this should be refactored into scanner_hardware
            #
            if GLB.config.get_bool_or('Scanning', 'simulating', False):
                hsn = GLB.db.get_highest_image_num(GLB.config['Election']['maximagenum'])
                self.next_seq_num = hsn if hsn is not None else 0
            else:
                self.next_seq_num = GLB.scanner.get_next_to_scan_new_batch()

            bsb.next_seq_num_in_batch = self.next_seq_num
            self.next_seq_numSB.setValue(int(self.next_seq_num))

        GLB.scanner.scan_a_batch()
        return True

    # TODO VERY IMPORTANT: How should handle the situation where the database and the directories disagree?
    # 1) it should be displayed
    # 2) We should already be able to recover if there are images on the disk not in the database???
    # 3) If the there are images in the database, not in the images the notification screen should include the Elections batch number

    # ----------------------  exit_check  ----------------------

    def exit_check(self, departureType='continue'):
        """Test for consistency among Admin settings. Return True if the transition should continue.
           e.g., no error or user response was "ignore"."""

        # Todo: next time: Add this elections batch num to accumulated electionsbatches.
        
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


    from transitioner import Transitioner_for_testing

    config = Scanconfig('etp.ini')
    app = QApplication(sys.argv)
    scanner = scanner_control.Scanner(config)
    transitioner = Transitioner_for_testing()
    transitioner.add_widget_main_panels(Scanning(config, QCoreApplication.quit,
                                                 "res/ui/scanning.ui", scanner, transitioner),
                                        "Scanning")
    transitioner.set_current_panel('Scanning')
    window = transitioner.main_panel_stack
    window.show()
    app.exec_()
