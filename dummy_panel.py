
'''Dummy Panel for testing

'''

from etpconfig import Scanconfig
from ETP_util import msgBox
import os
from PyQt5 import uic
from PyQt5.QtCore import QDateTime, QCoreApplication
from PyQt5.QtWidgets import QWidget, QDateTimeEdit
from PyQt5.QtWidgets import QMessageBox, QApplication
import sys
from transitioner import *

class Dummy(QWidget):

    def __init__(self, exit_app, uicpath):
        super().__init__()
        self._ui(uicpath)
        self.exit_app = exit_app

        # populate the screen

        self.quit_appPBn.clicked.connect(exit_app)

    def _ui(self, uicpath):
        uic.loadUi(uicpath, self)

    # Signal handlers

    # def dummy_transition(self):
    #     print('dummy transition error result = ' + str(self.exit_check()))
    #
    def entry_check(self):
        """Called from transitioner before switching to this screen. Return is a bool indicating
           whether it is OK to enter."""
        return True

    # screen and config consistency check

    def exit_check(self, departureType='continue'):
        return True # OK to proceed.

if __name__== '__main__':
    app = QApplication(sys.argv)
    config = Scanconfig('etp.ini')
    window = Dummy(QCoreApplication.quit, "res/ui/dummy.ui")
    window.show()
    app.exec_()


