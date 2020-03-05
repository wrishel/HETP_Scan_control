# note: thread.run() is blocked until the thread exits.

from PyQt5.QtCore import QCoreApplication, QObject, QRunnable, QThread, \
                          QThreadPool, pyqtSignal
import sys
import time

class AThread():
    def __init__(self):
        super().__init__()

    def run(self):
        count = 0
        while count < 5:
            time.sleep(1)
            print("A Increasing")
            count += 1

def texit():
    print('texit')

app = QCoreApplication([])
thread = AThread()
print(thread.isFinished())

thread.finished.connect(texit)
print('about to run thread')


# class AThread(QThread):
#     def __init__(self):
#         super().__init__()
#
#     def run(self):
#         count = 0
#         while count < 5:
#             time.sleep(1)
#             print("A Increasing")
#             count += 1
#
# def texit():
#     print('texit')
#
# app = QCoreApplication([])
# thread = AThread()
# print(thread.isFinished())
#
# thread.finished.connect(texit)
# print('about to run thread')
# thread.run()
print("I was hoping to see this come out before the first 'A Increasing'")
