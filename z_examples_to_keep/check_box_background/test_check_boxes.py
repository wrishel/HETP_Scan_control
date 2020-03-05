
# see https://stackoverflow.com/questions/59241645/background-color-of-qcheckbox-differs-when-checked-by-user-vs-when-python-code-s/59273624#59273624
# import inspect
# from PyQt5 import Qt
# vers = ['%s = %s' % (k,v) for k,v in vars(Qt).items() if k.lower().find('version') >= 0 and not inspect.isbuiltin(v)]
# print('\n'.join(sorted(vers)))
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5 import QtWidgets, uic

class X(QtWidgets.QTableWidget):
    def __init__(self, ui_file):
        super(X, self).__init__()
        uic.loadUi(ui_file, self)
        QTimer.singleShot(500, lambda: self.setwithPythoncode.setChecked(True))


if __name__== '__main__':
    app = QApplication([''])
    window = X("test_check_boxes.ui")
    window.show()
    app.exec_()
