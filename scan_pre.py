
'''Prescan panel: Mainpanals page for the operator to start scanning
'''
from datetime import datetime, timedelta
from etpconfig import Scanconfig
from ETP_util import msgBox, construct_list_text
import GLB_globals
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMessageBox, QWidget, QApplication
import sys

GLB = GLB_globals.get()

# todo: if time Designer changes to make the three entry boxes the same size and smaller.

class ScanPre(QWidget):
    """Pre-scan panel"""

    def __init__(self, exit_app, uicpath):
        super().__init__()
        self._ui(uicpath)
        self.exit_app = exit_app
        self.opid = None
        self.opid_list = list()
        self.unusual_next_seq_num_ok = False  # true if we've already challenged the next seq num

        # populate the screen
        # todo: if time move list and keyerror functionality into etpconfig.py

        if GLB.XXXDBG:
            self.operatorLE.setText('qqq')
            # self.elections_batch_numLE.setText('123')       # todo: polishing: this doesn't work

        # set signal connections AFTER initial values loaded

        self.operatorLE.editingFinished.connect(self.edit_opid)
        self.elections_batch_numLE.editingFinished.connect(self.elections_batch_num_changed)
        self.quitPB.clicked.connect(exit_app)  # todo: IMPORTANT Jump to close-app screen
        self.scanPB.clicked.connect(self.scanPB_pressed)

        # self.operatorLE.setFocus()  DOESN"T WORK HERE. THE SCREEN MUST BE DISPLAYED.

    def _ui(self, uicpath):
        import os
        x = os.getcwd()
        uic.loadUi(uicpath, self)
        # self.show()

    # ----------------------- signal handling -----------------------

    def edit_opid(self):
        """Edit the operator ID after it has changed."""

        new_opid = self.operatorLE.text()
        if new_opid in self.opid_list:
            self.opid = new_opid
            return True

        else:
            mbox = QMessageBox()
            mbox.setWindowTitle('Notification')
            mbox.setText('Is this the first time you entered your initials for this election?')
            mbox.setInformativeText(
                'If so, and if the initials you entered are correct, then press YES.\n\n' + \
                'If you entered the wrong initials, press CANCEL and re-enter them.')
            mbox.setDetailedText('')
            mbox.setIcon(QMessageBox.Question)
            mbox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            mbox.setDefaultButton(QMessageBox.Cancel)
            resp = mbox.exec()
            if resp == QMessageBox.Cancel:
                return False

            if resp == QMessageBox.Yes:
                self.opid = new_opid
                self.opid_list.append(new_opid)
                return True

            assert False, "Should never get here"

    def elections_batch_num_changed(self):
        # todo: need to validate the new value
            ...   # will get value directly from the widget at exit_check

    def scanPB_pressed(self):
        """User has pressed the SCAN button."""

        GLB.transitioner.set_current_panel('scanning')

    # ----------------------- entry_check -----------------------

    def entry_check(self):
        """Called from transitioner before switching to this screen. Return is a bool indicating
           whether it is OK to enter."""

        self.unusual_next_seq_num_ok = False
        self.elections_batch_numLE.setText('')
        GLB.batch_status.elections_batch_num = ''
        self.opid_list = GLB.config.get_list('Scanning', 'operatoridlist')
        self.next_seq_numSB.setValue(GLB.scanner.get_next_image_number()) # next sequence number
        if GLB.XXXDBG:
            self.elections_batch_numLE.setText('X')
        return True

    # ----------------------- exit_check -----------------------

    def exit_check(self):
        """Return True if the operation should continue. e.g., no error
           or user response was 'ignore'. """

        # Check for any of the line edits being empty and give flak.
        # Put all the empties found into a single error message.

        non_empties = {self.operatorLE: 'Operator ID',
                       self.elections_batch_numLE: 'Elections Batch Number',
                       self.next_seq_numSB: 'Next Sequence Number'}

        empties = []
        for box in non_empties.keys():
            if box.text() == '':
                empties.append(non_empties[box])

        empties_text = construct_list_text(empties)
        if empties_text != '':
            msg = f'{empties_text} boxes must have values.'
            msgInformativeText = 'Press CANCEL amd fill each of the boxes.'
            msgIcon = QMessageBox.Critical
            msgButtons = QMessageBox.Cancel
            msgDefaultButton = QMessageBox.Cancel
            msgDetails = ''
            res = msgBox(msg, msgInformativeText, msgIcon, msgDetails, msgButtons, msgDefaultButton)

            return False

        # todo: validate starting batch number

        # validate the operator ID. We already know it is in config['Scanning']['operatoridlist]
        # get operator id and validate by time
        # self.opid is the value entered or defaulted forward this time.
        # lastid the value in config, which is what was used on the last run

        mins90 = timedelta(minutes=90)
        now = datetime.now().replace(microsecond=0, second=0)
        # todo: implement what's below or get rid of it
        # lastid = GLB.config['Scanning']['operatorid']
        # last_time = datetime.fromisoformat(GLB.config['Scanning']['operatoriddatetime'])
        # timediff = now - last_time
        # if self.opid != lastid or timediff > mins90:
        #     msg = f'Please confirm that "{self.opid}" is the correct operator initials.'
        #     msgInformativeText = 'If it is correct press YES. if not' \
        #                          'press CANCEL and correct it.'
        #     msgIcon = QMessageBox.Question
        #     msgButtons = QMessageBox.Cancel | QMessageBox.Yes
        #     msgDefaultButton = QMessageBox.Cancel
        #     msgDetails = ''
        #     res = msgBox(msg, msgInformativeText, msgIcon, msgDetails, msgButtons, msgDefaultButton)
        #     if res == QMessageBox.Cancel:
        #         return False

        # check for starting batch on odd sequence number for double-sided ballots

        if self.unusual_next_seq_num_ok == False:
            if int(self.next_seq_numSB.text()) % 2 == 1 and bool(GLB.config['ballot']['doublesided']):
                msg = 'We are scanning double-sided ballots and the next sequence number is odd.\n\n' \
                      'This usually indicates a problem since the front sides of ballots have even numbers.\n\n'
                msgInformativeText = 'Please press CANCEL to get help. If you have been told to press IGNORE '\
                                      'Then do so.'
                msgIcon = QMessageBox.Question
                msgButtons = QMessageBox.Cancel | QMessageBox.Ignore
                msgDefaultButton = QMessageBox.Cancel
                msgDetails = ''
                res = msgBox(msg, msgInformativeText, msgIcon, msgDetails, msgButtons, msgDefaultButton)
                if res == QMessageBox.Cancel:
                    return False

                self.unusual_next_seq_num_ok = True

        # Write changes to config file and then return True

        sc = GLB.config['Scanning']
        GLB.batch_status.operator_id = self.opid
        sc['operatoriddatetime'] = now.isoformat(' ')
        sc['operatoridlist'] = '|'.join(self.opid_list)
        GLB.config.write()

        GLB.batch_status.elections_batch_num = self.elections_batch_numLE.text()
        # todo polishing embed special formatting of parameters list list, time in config object
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

    GLB = GLB_globals.get()
    GLB.set_object_instances()

    app = QApplication(sys.argv)
    scanner = GLB.scanner
    GLB.transitioner = Transitioner_for_testing()  # override the usual value for testing
    GLB.transitioner.add_widget_main_panels(ScanPre(QCoreApplication.quit,
                                                "res/ui/scan_pre.ui"),
                                        'scan_pre')
    GLB.transitioner.set_current_panel('scan_pre')
    window = GLB.transitioner.main_panel_stack
    window.show()
    app.exec_()
