"""Collection of signal definitions used in HETP scanning app"""

from PyQt5.QtCore import pyqtSignal, QObject
import GLB_globals
GLB = GLB_globals.get()


class QuSigs(QObject):
    scan_complete = pyqtSignal()        # scanning has completed a batch
    scan_error = pyqtSignal()           # scanning has discovered an error
    scan_update = pyqtSignal()          # scanning provides a mid-batch update
    inspector_viewing = pyqtSignal(str) # what image is the ballot inspector viewing

GLB.register(QuSigs(), 'signals')
