

'''Top Panel behaviors for HETP

   The top panel widget is contained in the .ui file for the MainWindow. Its
   behaviors are separated here for modularity.

   Each button controls a major process: Startup, Scan, Reports, and Shut Down.
   In addition, there is a fifth major process, Sustem Administration, which works
   like the others but doesn't have a button.

   When one of the buttons here is pressed, Top Panel calls the currently running
   process exit_ok method which either puts up error messages then returns false
   or returns true.'''


from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys

# TODO horizontal alignment and uniform fonts

qt_creator_file = "res/ui/toppanel.ui"

active_button_styleSheet = "background-color: rgb(247, 165, 255);"
inactive_button_styleSheet = "background-color: white;"

class TopPanel(QtWidgets.QWidget):

    def __init__(self):
        super(TopPanel, self).__init__()
        uic.loadUi(qt_creator_file, self)
        self.category_dict = {'Start Up': self.startUpButton, 'Scan': self.scanButton,
                              'Reports': self.reportsButton, 'Shut Down': self.shutdownButton}

    def show_active(self, active_wdg_name):
        active = self.category_dict.get(active_wdg_name, None)
        for wdgt in self.category_dict.values():
            if wdgt == active:
                wdgt.setStyleSheet(active_button_styleSheet)
            else:
                wdgt.setStyleSheet(inactive_button_styleSheet)
                # print(inactive_button_styleSheet, file=sys.stderr)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = TopPanel()
    window.show()
    app.exec_()
