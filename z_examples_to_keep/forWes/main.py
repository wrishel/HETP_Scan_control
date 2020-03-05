
from QtImageViewer_wes import QtImageViewer

from PyQt5 import QtCore, QtGui, QtWidgets, Qt

#from PyQt5.QtCore import Qt, QT_VERSION_STR
#from PyQt5.QtGui import QImage


#import the main window class for the generated code
from generated_4 import Ui_MainWindow


def modify_generated_ui(ui_main_window):
    #reference into the generated code, using pre-defined names to map to various controls
    #this should be part of a Class to avoid all these dangerous globals!

    ui_main_window.qtimageviewer = QtImageViewer()
    # Set the viewer's scroll bar behaviour.
    ui_main_window.qtimageviewer.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
    ui_main_window.qtimageviewer.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

    # Allow zooming with right mouse button.
    # Drag for zoom box, doubleclick to view full image.
    ui_main_window.qtimageviewer.canZoom = True

    # Allow panning with left mouse button.
    ui_main_window.qtimageviewer.canPan = True
    ui_main_window.hlImage.addWidget(ui_main_window.qtimageviewer)

    #add in button hooks
    #these names have to match the UI generated controls code
    ui_main_window.zoomIn.clicked.connect(respond_to_zoom_in_button)
    ui_main_window.zoomOut.clicked.connect(respond_to_zoom_out_button)

def respond_to_load_image_button():

    # Use Qt dialog to Load an image to be displayed.

    # fileName, dummy = QtWidgets.QFileDialog.getOpenFileName(None, "Open image file...")
    fileName = "/Users/Wes/Dropbox/Programming/ElectionTransparency/NewUI/NewUI_stacked/test_data/000000.jpg"
    image = QtGui.QImage(fileName)

    # Display the image in the viewer.
    main_ui.qtimageviewer.setImage(image)
    
def respond_to_zoom_in_button():
    main_ui.qtimageviewer.zoom_in_out(1, 0.10)

def respond_to_zoom_out_button():
    main_ui.qtimageviewer.zoom_in_out(-1, 0.10)

if __name__ == "__main__":

    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    
    #dpm - instantiate the main window as python object but not yet hooked to Qt
    main_ui = Ui_MainWindow()

    #perform the setup as defined by generated UI code
    #this also connects the UI generated code to our application and MainWindow
    main_ui.setupUi(MainWindow)

    #add our custom modifications
    # will add our custom widget to a placeholder container
    # will add hooks to our code for user actions
    modify_generated_ui(main_ui)

    MainWindow.show()
    respond_to_load_image_button()
    sys.exit(app.exec_())