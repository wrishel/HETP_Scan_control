from PyQt5.QtCore import QTimer, QCoreApplication
import sys

class Scanner(object):
    def __init__(self, app):
        self.num = -1
        self.app = app

    def simulated_item(self):
        self.num += 1
        print("item", self.num)
        if self.num <= 4:
            QTimer.singleShot(500, self.simulated_item)
        else:
            self.app.exit()

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    scnr = Scanner(app)
    scnr.simulated_item()
    sys.exit(app.exec_())

