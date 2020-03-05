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

# TODO Make main window sizing dynamic which means making subwidgets dynamic
# TODO Gray gap between green and yellow panels
# TODO Make all buttons uniform color, such as rgb(226, 255, 255);
# TODO: important: eliminate all references to auto backup

import datetime
import os
import signal
import subprocess
import time

print(datetime.datetime.now().isoformat(' '))   # for debugging

# from dummy_panel import Dummy
import GLB_globals
import os
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
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
