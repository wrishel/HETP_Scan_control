from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt5.QtWidgets import QGridLayout, QWidget, QDesktopWidget
import sys

class main(QWidget):
    def __init__(self):
        super().__init__()
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        qtRectangle = self.frameGeometry()
        self.move(100, 100)

if __name__== '__main__':
    app = QApplication(sys.argv)
    window = main()
    window.show()
    app.exec()

