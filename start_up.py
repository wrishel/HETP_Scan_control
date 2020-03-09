
'''Start up panel

Mainpanals page for the scanning user. Normally run once a day.

Maintains the scanning.ini file among other things.

'''

from etpconfig import Scanconfig
from ETP_util import msgBox
import GLB_globals
import os
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox, QApplication
import sys

GLB = GLB_globals.get()

class DateTimeEditUpdater():
    """This is an attempt to update a QDateTimeEdit to show the current time without
       stepping on changes that the user is entering from the keyboard.

       Uses a timer to update approximately once a minute unless the value was changed
       somewhere else. If the value was changed somewhere else than increment it"""

    def __init__(self, qdte):
        """qdte is a QDateTimeEdit widget. initial_value is the contents when this is called."""
                            # todo: calendar popup, diable updating while it's open
        self.qdte = qdte
        self.qdte.setDateTime(QDateTime.currentDateTime())
        self.period = 1000
        self.ticking = False

    def enable(self):
        self.ticking = True
        self.tick()

    def disable(self):
        self.ticking = False

    def tick(self):
        """Increment the widget time"""

        if not self.ticking: return
        new_time = self.qdte.dateTime().addMSecs(self.period)
        self.qdte.setDateTime(new_time)
        QTimer.singleShot(self.period, self.tick)   # check back in period msecs


class StartUp(QWidget):
    check_boxes = {   # translate the object name of a widget to the heading in the .ini file
        'datetimeCB': 'dateTimek',
        'ballot_paramsCB': 'ballotScanningParams',
        'electionTitleCB': 'ballotTitleOk', #'backupCB': 'ballotBackupRequested',
        'thicknessCB': 'thicknessOk',
        'imprinterCB': 'imprinterOk'
    }
    check_box_error_names = {   # translate the object names to language for error message
        'datetimeCB': 'current date and time','ballot_paramsCB': 'ballot length and number of sides',
        'electionTitleCB': 'election title',
        'thicknessCB': 'ballot thickness', 'imprinterCB': 'imprinter position on scanner'
    }

    def __init__(self, config, exit_app, uicpath):
        super().__init__()
        self._ui(uicpath)
        self.exit_app = exit_app
        self.date_time_updater =  DateTimeEditUpdater(self.date_timeEdit)
        if GLB.XXXDBG: self.datetimeCB.setChecked(True)

        # set signal connections AFTER initial values loaded
        for cb_name in self.check_boxes.keys():
            cb = getattr(self, cb_name)
            cb.toggled.connect(lambda: self.cb_toggled(cb))

        self.quit_appPBn.clicked.connect(exit_app)
        self.begin_scanningPB.clicked.connect(self.begin_scanning)
        self.test_scanPB.pressed.connect(self.scan_test_ballot)

    def _ui(self, uicpath):
        uic.loadUi(uicpath, self)

    # Signal handlers

    def cb_toggled(self, cb):
        """Handle a checkbox being changed.  cb is the checkbox itself"""

        GLB.config['Setup'][self.check_boxes[cb.objectName()]] = str(cb.isChecked())
        GLB.config.write()   # TODO: When initially loading config, clear certain checkbox values in it

    def scan_test_ballot(self):
        GLB.scanner.scan_test_ballot()

    def begin_scanning(self):
        GLB.transitioner.set_current_panel("scan_pre")


    def entry_check(self):
        """Called from transitioner before switching to this screen. Return is a bool indicating
           whether it is OK to enter."""
           # todo: move some of the __init__ logic here.

        # populate the screen
        s = 'DOUBLE SIDED.' if GLB.config['ballot']['doublesided'] else 'SINGLE SIDED.'
        self.ballot_paramstLBL.setText(GLB.config['Election']['title'])

        # Match check box object names with the config file keys and set the value on the screen.
        for cb_name in self.check_boxes.keys():
            config_file_key = self.check_boxes[cb_name]
            if config_file_key in GLB.config['Setup']:
                config_value = GLB.config['Setup'][config_file_key]
                cb_object = getattr(self, cb_name)
                cb_object.setChecked(config_value == 'True')


        self.date_time_updater.enable()
        return True

    def exit_check(self):
        """Called by transitioner. Returns True if the operation should continue.
           E.g., no error or user response was "ignore"."""

        # todo: polishing highlight the boxes that are the subject of messages
        # todo: someday move all message text to a separate module

        self.date_time_updater.disable()

        # see if certain checkboxes are not checked.
        squawks = []
        squawk_list = {'datetimeCB': 'current date and time','ballot_paramsCB': 'ballot length and number of sides',
                       'electionTitleCB': 'election title', 'thicknessCB': 'ballot thickness',
                       'imprinterCB': 'imprinter position on scanner'}

        for cb_name in squawk_list.keys():
            cb_object = getattr(self, cb_name)
            if not cb_object.isChecked():
                squawks.append(self.check_box_error_names[cb_name])

        if len(squawks):
            if len(squawks) == 1: msg = "This box is not checked: '" + squawks[0] + "'."
            else: msg = "These boxes are not checked: '" + "', '".join(squawks) + "'"
            resp = msgBox(msg,
                       "Each of the listed checkboxes represent something that must be correct "
                       "for scanning to work.\n\nAfter the first day of scanning "
                       "it's usually OK to assume that these are OK unless the scanner "
                       "was used somewhere else. So if this is not the first run try "
                       "pressing Cancel, going back and checking these boxes, and "
                       "pressihg BEGIN SCANNING again.",
                       QMessageBox.Question, '',  QMessageBox.Cancel,
                       QMessageBox.Cancel
                   )
            if resp == QMessageBox.Cancel: return False
            # else continue to other error checks

        # backups not implemented yet
        if False: # backing up not implemented yet
            ext = GLB.config.get_bool_or('Election','pathtoextdrive', None)
            if self.backupCB.isChecked():
                if bool(ext):
                    if not os.path.isdir(ext):
                        msg = "Can't operate because the external drive is not available for backups."
                        resp = msgBox(msg,
                           # msgInformativeText
                               "Check to see if the external drive is turned on and connected." \
                               "\n\nIf not check with a system administrator."
                               "\n\nIn a pinch press Cancel, uncheck the box and press "
                               "BEGIN SCANNING again.",
                           #  msgicon
                                  QMessageBox.Question,
                           # msg details
                                '',
                           # msgbuttons
                               QMessageBox.Ignore | QMessageBox.Ignore,
                           # msgbuttondefault
                               QMessageBox.Ignore
                        )

                else: # config does not have a path set up.
                    msgtext = "Please uncheck the box for backups to the external drive."
                    msginformativetext = "The system is currently not setup for backups."
                    msgicon = QMessageBox.Warning
                    msgmoreinfo = ''
                    msgbuttons = QMessageBox.Cancel
                    msgbuttondefault = QMessageBox.Cancel

                    resp = msgBox(msgtext, msginformativetext, msgicon, msgmoreinfo,
                                  msgbuttons, msgbuttondefault)

                    return False    # not OK to proceed

            else: # box not checked
                if  os.path.isdir(ext): # is backup spec in config and present?
                    msgtext = "Do you want backups to the external drive?"
                    msginformativetext = "The current setup calls for these backups but the box is not" \
                         "checked. If you meant to skip backups this time, then press No. " \
                         "If you want to backups to happen, press Yes to go back, then check the box, and " \
                         "press BEGIN SCANNING again."
                    msgicon = QMessageBox.Warning
                    msgmoreinfo = ''
                    msgbuttons = QMessageBox.Yes | QMessageBox.No
                    msgbuttondefault = QMessageBox.Yes

                    resp = msgBox(msgtext, msginformativetext, msgicon, msgmoreinfo,
                                  msgbuttons, msgbuttondefault)

                    if resp == QMessageBox.Yes: return False    # not OK to proceed

        return True # OK to proceed.

if __name__== '__main__':

    from transitioner import dummy_transitioner

    t = dummy_transitioner.Transitioner()
    app = QApplication(sys.argv)
    config = Scanconfig('etp.ini')
    window = StartUp(config, QCoreApplication.quit, "res/ui/startup.ui", t)
    t.set_initial_panel(window)
    window.show()
    app.exec_()


