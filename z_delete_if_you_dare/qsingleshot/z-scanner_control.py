
# https://stackoverflow.com/questions/59637527/pyqt5-qtimer-singleshot-doesnt-run-at-all/59637757#59637757

from PyQt5.QtCore import QTimer, QCoreApplication, QThread
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
    thread = QThread()
    scnr = Scanner(app)
    thread.started.connect(scnr.simulated_item)
    thread.start()
    sys.exit(app.exec_())


# from PyQt5.QtCore import QTimer, QCoreApplication, QThread
# import time, sys
#
# class Scanner(object):
#     def __init__(self):
#         self.num = -1
#
#     def set_up_batch(self, operator_id, update_callback):
#         print('set_up_batch')
#         self.update_callback = update_callback
#         QTimer.singleShot(1, self.simulated_item)
#
#     def simulated_item(self):
#         print('item')
#         self.update_callback()
#         self.num += 1
#         if self.num > 4:
#             self.normal_stop_callback()
#             return
#         QTimer.singleShot(100, self.simulated_item)
#
# class dummy(QThread):
#     def update(self):
#         print('update')
#
#     def run(self):
#         scnr = Scanner()
#         scnr.set_up_batch('opid', self.update)
#         print('returned from set_up_batch')
#         for i in range(10):
#             time.sleep((0.2))
#
#
# app = QCoreApplication([])
# thread = dummy()
# thread.run()
#
#
#
