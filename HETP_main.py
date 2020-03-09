'''Example stacked widgets as objects with designer'''


# main.ui -> Ui_MainWindow
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                               #
#                toppanel.ui -> import top_panel.py             # 
#                    -> MainWindow.topPanel                     #
#                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                  #                                            #
#   Ui_MainWindow. #      panels =                              #
#    frame_2       #         various modules described below    #
#                  #                                            #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#                 ui file                  mainpanels
#   module name    name     class name     page name
#   -----------   -------   ----------     ----------
#     sysadmin    sysadmin  SysAdmin        sysadmin
#
#
#    The class name of each panel must be unique.

import datetime
import signal
import shutil
import subprocess
import time

print(datetime.datetime.now().isoformat(' '))   # for debugging

# The imports for singleton objects managed by GLB are ordered
# according to their implicit precedent requirements.

import GLB_globals
import os
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
from batch import Batch_status
from scanner_hardware import Scan_HW_Control
from dbase import ETPdb
from transitioner  import Transitioner
from scanning import Scanning
from scan_pre import ScanPre
from scan_post import ScanPost
from start_up import StartUp
from sys_admin import SysAdmin
from scan_error1 import ScanError1
from scan_error2 import ScanError2
# from scan_error3 import ScanError3

# various initializations are in Sysadmin.entry_check()


qt_creator_file = "./res/ui/main.ui"

GLB = GLB_globals.get()

# TODO: IMPORTANT: trap error exit and delete any batches backed over
#       send signals to running batch processes
#       wait one second and then kill them

class MainWindow(QtWidgets.QMainWindow):
    """Main for the UI. All panels and global objects are set up here."""

    def __init__(self):
        super().__init__()
        uic.loadUi(qt_creator_file, self)
        GLB.db.connect(GLB.config['Debugging']['database'])
        GLB.scanner.init_more()

        GLB.main_window = self
        GLB.transitioner.main_panel_stack = self.main_panels

        # load the panels and register them with transitioner

        if bool(GLB.config['Debugging']['sys_admin']):
            sysadmin = SysAdmin(self.exit_app, "res/ui/sysadmin.ui")
            GLB.transitioner.add_widget_main_panels(sysadmin, 'Sys Admin')

        startup = StartUp(GLB.config, self.exit_app, "res/ui/startup.ui")
        GLB.transitioner.add_widget_main_panels(startup, 'Start Up')

        scan_pre = ScanPre(self.exit_app, "res/ui/scan_pre.ui")
        GLB.transitioner.add_widget_main_panels(scan_pre, 'scan_pre')

        scanner = Scanning(self.exit_app, "res/ui/scanning.ui")
        GLB.transitioner.add_widget_main_panels(scanner, 'scanning')

        scan_post = ScanPost(self.exit_app, "res/ui/scan_post.ui")
        GLB.transitioner.add_widget_main_panels(scan_post, 'scan_post')

        scan_error1 = ScanError1(self.exit_app, "res/ui/scan_error.ui")
        GLB.transitioner.add_widget_main_panels(scan_error1, 'scan_error1')

        scan_error2 = ScanError2(self.exit_app, "res/ui/scan_error_2.ui", self.main_panels)
        GLB.transitioner.add_widget_main_panels(scan_error2, 'scan_error2')

        if bool(GLB.config['Debugging']['sys_admin']) =='True':
            GLB.transitioner.set_current_panel('Sys Admin')
        else:
            GLB.transitioner.set_current_panel('Start Up')


        # activate the testing or production database
        db_choice = GLB.config.get_or_else('Debugging', 'database', 'testing, None')
        GLB.db.connect(db_choice)

        # for testing, clear images from the database and delete spoiled images
        if GLB.config.get_bool_or("Debugging", 'clear_db_on_start', False):
            GLB.db.recreate_images()   # clear the database
            spoiled_path = GLB.config['Election']['path_to_spoiled_images']
            for root, dirs, files in os.walk(spoiled_path):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))

            # GLB.config["Debugging"]['clear_db_on_start'] = 'False'
            # GLB.config.write()


        GLB.db.fix_orphaned_rows()


        # start parallel processes
        #
        self.ext_processes = []
        num_bars = int(GLB.config.get_or_else('Processes', 'num_barcode_processes', 0))
        exe_path = f'{os.getcwd()}/process_barcodes.py'
        print(exe_path)
        #                           Popen(["/usr/bin/git", "commit", "-m", "Fixes a bug."])
        for i in range(num_bars):
            self.ext_processes.append(subprocess.Popen([exe_path]))

        for p in self.ext_processes:
            print({f'barcode process: {p.pid}'}, file=sys.stderr)

    def exit_app(self):
        for i in range(len(self.ext_processes)):
            p = self.ext_processes[i]
            p.send_signal(signal.SIGINT)

        if len(self.ext_processes):
                time.sleep(2)  # give the processes some time to wrap up

        QtCore.QCoreApplication.quit()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
print(f"app exits with value: {app.exec_()}", file=sys.stderr)
