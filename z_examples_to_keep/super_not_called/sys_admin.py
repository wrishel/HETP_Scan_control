
'''Sysadmin panel

Mainpanals page for the system administrator. Various set up functions
for an election.

Maintains the etp.ini file among other things.

Not accessible to normal users.
'''

from etpconfig import Scanconfig
import os
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMessageBox, QWidget, QApplication
import sys

class SysAdmin(QWidget):
    CBVALUES = ['False', None, 'True']      # I wish I knew how to use the qt enum
    LENGTHSENDERS = {'size11RB': 11, 'size14RB': 14, 'size17RB': 17, 'size21RB': 21}

    def __init__(self, exit_app, uicpath):
        super().__init__()
        self._ui(uicpath)
        self.config = config
        self.exit_app = exit_app
        try:
            # populate the screen
            self.electionTitleLE.setText(self.config['Election']['Title'])
            self.pathToImagesLE.setText(self.config['Election']['pathtoimages'])
            self.pathToExtDriveLE.setText(self.config['Election']['pathtoextdrive'])
            self.doubleSidedCB.setChecked((self.config['ballot']['DoubleSided']) == 'True')
            self.firstTimeCheckBox.setChecked(self.config['Election']['firstrun'] == 'True')

            # populate the check box to corresponding to length
            length = int(self.config['ballot']['Length'])  # check for not in file at all
            for key, value in self.LENGTHSENDERS.items():
                if value == length:
                    getattr(self, key).setChecked(True)
                    break

        except KeyError as e:
            print('ERROR: Unable to find key ' + str(e) +
                  ' in configuration file')
            exit(1)

        # # TODO change path widgets to file openers

        # set signal connections AFTER initial values loaded
        self.operatorExitPB.pressed.connect(exit_app)
        self.doubleSidedCB.stateChanged.connect(self.changeDoubleSided)
        self.electionTitleLE.textChanged.connect(self.changeTitle)
        self.pathToExtDriveLE.textChanged.connect(self.changePathToExtDrive)
        self.pathToImagesLE.textChanged.connect(self.changePathToImages)
        self.firstTimeCheckBox.stateChanged.connect(self.changeFirstRun)
        self.operatorStartupPB.pressed.connect(exit_app)

        for cb in self.LENGTHSENDERS.keys():  # connect all length checkboxes
            getattr(self, cb).toggled.connect(self.lengthBoxChecked)

        self.operatorStartupPB.pressed.connect(self.proceed_to_startup)

    def _ui(self, uicpath):
        import os
        x = os.getcwd()
        uic.loadUi(uicpath, self)
        # self.show()

    # signal handling methods

    def changeDoubleSided(self, int):
        self.config['ballot']['DoubleSided'] = self.CBVALUES[self.doubleSidedCB.checkState()]
        self.config.write()

    def changeFirstRun(self, int):
        self.config['Election']['firstrun'] = self.CBVALUES[int]
        self.config.write()

    def lengthBoxChecked(self):
        sender = self.sender()
        length = self.LENGTHSENDERS.get(sender.objectName(), None)
        assert length, 'invalid length check box name'
        self.config['ballot']['Length'] = str(length)
        self.config.write()

    def changeTitle(self, newValue):
        self.config['Election']['title'] = newValue
        self.config.write()

    def changePathToExtDrive(self, newValue):
        self.config['Election']['pathtoextdrive'] = newValue
        self.config.write()

    def changePathToImages(self, newValue):
        self.config['Election']['pathtoimages'] = newValue
        self.config.write()

    def proceed_to_startup(self):
        GLB.transitioner.set_current_panel('Start Up')

    # validity checking

    def entry_check(self):
        """Called from transitioner before switching to this screen. Return is a bool indicating
           whether it is OK to enter."""
            # todo: move some of the __init__ logic here.
        return True

    def exit_check(self):
        """Test for consistency among Admin settings. Return True if the operation should continue.
           i.e., no error or user response was "ignore"."""

        imagedir = self.config['Election']['pathtoimages']
        backupdir = self.config['Election']['pathtoextdrive']
        if self.config['Election']['firstrun']  == 'True':
            if os.path.isdir(imagedir):
                if len(os.listdir(imagedir) ) == 0:
                    pass    # this is OK
                else:
                    resp = self.msgBox('Files already in image directory',
                            'When "First Run" is checked the Path to Images should be an empty directory.' +
                                '\n\nPress "Details" for more information',
                                QMessageBox.Critical,
                                'Is this really the first run of the election? If not, press cancel then '
                                'uncheck the "First Run" box.'
                                '\n\nIf xo, Press "Cancel" and yell at the Administrator.',
                                QMessageBox.Cancel|QMessageBox.Ignore)

                    if resp == QMessageBox.Cancel:
                        return False

        else:  # firstrun not checked
            if not os.path.isdir(imagedir):
                resp = self.msgBox('Image path is not a directory',
                           'The path to images that the Administrator set up is "' + imagedir +
                            '", which is not a valid, existing directory. ' +
                            '\n\nPress "Cancel" and yell at the Administrator.',
                            QMessageBox.Critical, '', QMessageBox.Cancel)

                return False

        if backupdir.strip() == '':
            resp = self.msgBox('Backup path to external drive not set.',
                               'The Administrator has left the Path to External Drive empty. ' +
                               'Backup images will not be automatically created durint this run. ' +
                               '\n\nIf the backup drive is there and connected to the computer ' +
                               'you may wamt to press Cancel and check with the ' +
                               'the Administrator'
                               '\n\nYou can also Press "Ignore" to go ahead. The backups can be ' +
                               'created later.',
                               QMessageBox.Warning, '', QMessageBox.Cancel | QMessageBox.Ignore)
            if resp == QMessageBox.Cancel:
                return False

        elif not os.path.isdir(backupdir):
            resp = self.msgBox('Backup path to an external drive is incorrect.',
                               imagedir + ' is wrong or perhaps the external drive is not online. ' +
                               '\n\nPress "Ignore" to go ahead any way. Backups can be made later.' +
                               '\n\nPress "Cancel to try to plug in or turn on the external drive',
                               QMessageBox.Warning, '', QMessageBox.Cancel | QMessageBox.Ignore)
            if resp == QMessageBox.Cancel:
                return False

        else: # path to external drive is not empty
            if not os.path.isdir(backupdir):
                resp = self.msgBox('Backup path to an external drive is not a directory',
                                   backupdir + ' should be a directory but is an error or perhaps ' +
                                   'the external drive is not set up.' +
                                   'Backup will not be automatically created durint this run, ' +
                                   'but they can be made later. ' +
                                   'Press "Ignore to go ahead any way.',
                                   QMessageBox.Warning, '', QMessageBox.Cancel | QMessageBox.Ignore)
                if resp == QMessageBox.Cancel:
                    return False

        if self.config['ballot']['length'].strip() == '':
            resp = self.msgBox('The Adminastratpor has not set the ballot length.',
                               '\n\nPress "Cancel" and yell at the Administrator.',
                               QMessageBox.Critical, '', QMessageBox.Cancel)
            return False

        return True


if __name__== '__main__':
    import scanner_control
    from transitioner import Transitioner_for_testing

    config = Scanconfig('etp.ini')
    app = QApplication(sys.argv)
    scanner = scanner_control.Scanner(config)
    transitioner = Transitioner_for_testing()
    # window = SysAdmin()
    window = SysAdmin(QCoreApplication.quit, "res/ui/sysadmin.ui")
    window.show()
    app.exec_()
