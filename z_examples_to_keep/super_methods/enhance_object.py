import sys
from PyQt5.Qt import *

class MyPopup(QWidget):
    def __init__(self, mainwin):
        QWidget.__init__(self)

        # I want to change the lable1 of MainWindow
        mainwin.label1.setText('hello')


class MainWindow(QMainWindow):
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        self.btn1 = QPushButton("Click me", self.cw)
        self.btn1.setGeometry(QRect(50, 50, 100, 30))
        self.label1 = QLabel("No Commands running", self.cw)
        self.btn1.clicked.connect(self.doit)
        self.w = None

    def doit(self):
        self.w = MyPopup(self)
        self.w.setGeometry(QRect(100, 100, 400, 200))
        self.w.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())