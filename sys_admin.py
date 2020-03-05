
'''Sysadmin panel

Mainpanals page for the system administrator. Various set up functions
for an election.

Maintains the etp.ini file among other things.

Not accessible to normal users.
'''

from etpconfig import Scanconfig
from ETP_util import msgBox
import GLB_globals
import os
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMessageBox, QWidget, QApplication
import sys

GLB = GLB_globals.get()

class SysAdmin(QWidget):
    CBVALUES = ['False', None, 'True']      # I wish I knew how to use the qt enum
    LENGTHSENDERS = {'size11RB': 11, 'size14RB': 14, 'size17RB': 17, 'size21RB': 21}

    def __init__(self, exit_app, uicpath):
        super().__init__()

        self._ui(uicpath)
        self.exit_app = exit_app
        try:
            # populate the screen
            self.electionTitleLE.setText(GLB.config['Election']['Title'])
            self.pathToImagesLE.setText(GLB.config['Election']['pathtoimages'])
            self.pathToExtDriveLE.setText(GLB.config['Election']['pathtoextdrive'])
            self.doubleSidedCB.setChecked((GLB.config['ballot']['DoubleSided']) == 'True')
            self.firstTimeCheckBox.setChecked(GLB.config['Election']['firstrun'] == 'True')

            # populate the check box to corresponding to length
            length = int(GLB.config['ballot']['Length'])  # check for not in file at all
            for key, value in self.LENGTHSENDERS.items():
                if value == length:
                    getattr(self, key).setChecked(True)
                    break

        except KeyError as e:
            print('ERROR: Unable to find key ' + str(e) + ' in configuration file')
            exit(1)

        # TODO change path widgets to file openers

        # set signal connections AFTER initial values loaded
        self.operatorExitPB.pressed.connect(exit_app)
        self.doubleSidedCB.stateChanged.connect(self.changeDoubleSided)
        self.electionTitleLE.textChanged.connect(self.changeTitle)
        self.pathToExtDriveLE.textChanged.connect(self.changePathToExtDrive)
        self.pathToImagesLE.textChanged.connect(self.changePathToImages)
        self.firstTimeCheckBox.stateChanged.connect(self.changeFirstRun)

        for cb in self.LENGTHSENDERS.keys():  # connect all length checkboxes
            getattr(self, cb).toggled.connect(self.lengthBoxChecked)

        self.operatorStartupPB.pressed.connect(self.proceed_to_startup)

        # self.proceed_to_startup()       # TODO: debugging shunt

    def _ui(self, uicpath):
        import os
        x = os.getcwd()
        uic.loadUi(uicpath, self)
        # self.show()

    # signal handling methods

    def changeDoubleSided(self, int):
        GLB.config['ballot']['DoubleSided'] = self.CBVALUES[self.doubleSidedCB.checkState()]
        GLB.config.write()

    def changeFirstRun(self, int):
        GLB.config['Election']['firstrun'] = self.CBVALUES[int]
        GLB.config.write()

    def lengthBoxChecked(self):
        sender = self.sender()
        length = self.LENGTHSENDERS.get(sender.objectName(), None)
        assert length, 'invalid length check box name'
        GLB.config['ballot']['Length'] = str(length)
        GLB.config.write()

    def changeTitle(self, newValue):
        GLB.config['Election']['title'] = newValue
        GLB.config.write()

    def changePathToExtDrive(self, newValue):
        GLB.config['Election']['pathtoextdrive'] = newValue
        GLB.config.write()

    def changePathToImages(self, newValue):
        GLB.config['Election']['pathtoimages'] = newValue
        GLB.config.write()

    def proceed_to_startup(self):
        GLB.transitioner.set_current_panel('Start Up')

    # validity checking

    def entry_check(self):
        """Called from transitioner before switching to this screen. Return is a bool indicating
           whether it is OK to enter."""
            # todo: move some of the __init__ logic here.

        # activate the testing or production database
        db_choice = GLB.config.get_or_else('Debugging', 'database', 'testing, None')
        GLB.db.connect(db_choice)
        max_img_num = GLB.config.get_or_else('Election', 'maximagenum', '999999', None)
        # actual_max =  GLB.db.get_highest_image_num(max_img_num)


        if GLB.config["Debugging"]['clear_db_on_start'] == 'True':
            GLB.db.recreate_images()   # clear the database
            GLB.config["Debugging"]['clear_db_on_start'] = 'False'
            GLB.config.write()

        GLB.db.fix_orphaned_rows()
        return True

    def exit_check(self, departureType='continue'):
        """Test for consistency among Admin settings. Return True if the operation should continue.
           i.e., no error or user response was "ignore"."""

        imagedir = GLB.config['Election']['pathtoimages']
        backupdir = GLB.config['Election']['pathtoextdrive']
        if GLB.config['Election']['firstrun']  == 'True':
            if os.path.isdir(imagedir):
                if len(os.listdir(imagedir) ) == 0:
                    pass    # this is OK
                else:
                    resp = msgBox('Files already in image directory',
                            'When "First Run" is checked the Path to Images should be an empty directory.' +
                                '\n\nPress "Details" for more information',
                                QMessageBox.Critical,
                                'Is this really the first run of the election? If not, press cancel then '
                                'uncheck the "First Run" box.'
                                '\n\nIf xo, Press "Cancel" and yell at the Administrator.',
                                QMessageBox.Cancel|QMessageBox.Ignore, QMessageBox.Cancel)

                    if resp == QMessageBox.Cancel:
                        return False

        else:  # firstrun not checked
            if not os.path.isdir(imagedir):
                resp = msgBox('Image path is not a directory',
                           'The path to images that the Administrator set up is "' + imagedir +
                            '", which is not a valid, existing directory. ' +
                            '\n\nPress "Cancel" and yell at the Administrator.',
                            QMessageBox.Critical, '', QMessageBox.Cancel, QMessageBox.Cancel)

                return False

        if backupdir.strip() == '':
            resp = msgBox('Backup path to external drive not set.',
                               'The Administrator has left the Path to External Drive empty. ' +
                               'Backup images will not be automatically created durint this run. ' +
                               '\n\nIf the backup drive is there and connected to the computer ' +
                               'you may wamt to press Cancel and check with the ' +
                               'the Administrator'
                               '\n\nYou can also Press "Ignore" to go ahead. The backups can be ' +
                               'created later.',
                               QMessageBox.Warning, '', QMessageBox.Cancel | QMessageBox.Ignore, QMessageBox.Cancel)
            if resp == QMessageBox.Cancel:
                return False

        elif not os.path.isdir(backupdir):
            resp = msgBox('Backup path to an external drive is incorrect.',
                               imagedir + ' is wrong or perhaps the external drive is not online. ' +
                               '\n\nPress "Ignore" to go ahead any way. Backups can be made later.' +
                               '\n\nPress "Cancel to try to plug in or turn on the external drive',
                               QMessageBox.Warning, '', QMessageBox.Cancel | QMessageBox.Ignore, QMessageBox.Cancel)
            if resp == QMessageBox.Cancel:
                return False

        else: # path to external drive is not empty
            if not os.path.isdir(backupdir):
                resp = msgBox('Backup path to an external drive is not a directory',
                                   backupdir + ' should be a directory but is an error or perhaps ' +
                                   'the external drive is not set up.' +
                                   'Backup will not be automatically created durint this run, ' +
                                   'but they can be made later. ' +
                                   'Press "Ignore to go ahead any way.',
                                   QMessageBox.Warning, '', QMessageBox.Cancel | QMessageBox.Ignore, QMessageBox.Cancel)
                if resp == QMessageBox.Cancel:
                    return False

        if GLB.config['ballot']['length'].strip() == '':
            resp = msgBox('The Adminastratpor has not set the ballot length.',
                               '\n\nPress "Cancel" and yell at the Administrator.',
                               QMessageBox.Critical, '', QMessageBox.Cancel)
            return False

        return True


if __name__== '__main__':
    from transitioner import Transitioner_for_testing

    GLB.set_object_instances()
    config = Scanconfig('etp.ini')
    app = QApplication(sys.argv)
    # scanner = scanner_control.Scanner(config)
    transitioner = Transitioner_for_testing()
    transitioner.add_widget_main_panels(SysAdmin(QCoreApplication.quit,
                                                 "res/ui/sysadmin.ui"),
                                        "Sysadmin")
    transitioner.set_current_panel('Sysadmin')
    window = transitioner.main_panel_stack
    window.show()
    app.exec_()
