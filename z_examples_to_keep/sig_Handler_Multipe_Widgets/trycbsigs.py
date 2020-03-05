
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets, uic
from os import getcwd

print(getcwd())
class X(QtWidgets.QTableWidget):
    def __init__(self, ui_file):
        super(X, self).__init__()
        uic.loadUi(ui_file, self)
        self.checkBox.clicked.connect(lambda:self.btnstate(self.checkBox))
        self.checkBox_2.clicked.connect(lambda:self.btnstate(self.checkBox_2))

    def btnstate(self, cb):
        """React to change in state of checkbox cb"""

        print(cb.objectName(), cb.isChecked())


if __name__== '__main__':
    app = QApplication([''])
    window = X("trycbsigs.ui")
    window.show()
    app.exec_()
