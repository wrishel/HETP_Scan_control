
# see https://stackoverflow.com/questions/59241645/background-color-of-qcheckbox-differs-when-checked-by-user-vs-when-python-code-s/59273624#59273624

# CURRENTLY DOESN'T WORK BECAUSE ex IS UNDEFINED

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QCheckBox
from PyQt5.QtCore import QEvent
from PyQt5 import QtWidgets

class MyApp(QApplication):

    def __init__(self, args):
        super().__init__(args)
        self.application_first_time_active = True# You need to know when is the first time application was activated
        self.target_object = None

    def setTargetObject(self, obj):
        self.target_object = obj

    def event(self, event):
         if event.type() == QEvent.ApplicationActivated and self.application_first_time_active:
             self.target_object.initialize()
             self.application_first_time_active = False
         return super().event(event)


class CheckDemo(QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.b1 = QCheckBox("Button1", self)
        self.b2 = QCheckBox("Button2", self)
        self.b3 = QCheckBox("Button3", self)

        self.layout.addWidget(self.b1)
        self.layout.addWidget(self.b2)
        self.layout.addWidget(self.b3)

        self.b1.setChecked(False)
        self.b2.setChecked(False)
        self.b3.setChecked(False)

        self.setLayout(self.layout)
        self.setWindowTitle("checkbox demo")

    def initialize(self):
        self.b2.setChecked(True)


def main():
    app = MyApp(sys.argv)
    customWidget = CheckDemo()
    app.setTargetObject(ex)
    customWidget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()