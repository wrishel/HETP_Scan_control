import sys
from PyQt5 import QtCore, QtWidgets

class MainWindow(QtWidgets.QWidget):
    def __init__(self, other_window=None):
        super().__init__()
        app = QtWidgets.QApplication.instance()
        desktop = app.desktop()
        avail_geom = desktop.availableGeometry()
        print('avail=',avail_geom,avail_geom.topRight())
        mid_line = int(avail_geom.width() / 2)
        # print(mid_line)
        my_size = self.size()
        # print('my size', my_size)
        if other_window is None:
            tentative_x = mid_line - self.size().width()
            x = max(0, tentative_x)
            self.move(x, 100)

        # todo: should layout both windows in the else clause and center vertically.

        else:
            self.resize(1000, 1000)
            right_side_space = avail_geom.width() - self.size().width()
            if right_side_space  > avail_geom.width():
                right_offset = -right_side_space
            else:
                right_offset = 0
            self.move(mid_line + right_offset, 100)
        ...

    def moveEvent(self, e):
        # print('move=', self.pos(),self.mapToGlobal(self.pos()))
        super(MainWindow, self).moveEvent(e)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    w1 = MainWindow(window)
    w1.show()
    sys.exit(app.exec_())