"""This is SOLUTION_1.py modified to import the widget_a.ui at run time.

   By itself it is still not the complete solution to the replicate_stacked error.

   In this code the the class we use inherits from QWidget and imports widget_a.ui.
   """



from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QWidget
import sys

class Ui_widgetA(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('widget_a.ui', self)


app = QtWidgets.QApplication(sys.argv)
main = Ui_widgetA()
main.show()
sys.exit(app.exec())