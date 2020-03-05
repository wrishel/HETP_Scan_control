""" QtImageViewer.py: PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.

"""
#
#modified by dpm for wes, Feb 2019
#my changes are marked with 'dpm' comment blocks
#

import os.path
try:
    from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QT_VERSION_STR

    from PyQt5.QtGui import QImage, QPixmap, QPainterPath
    from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QFileDialog
except ImportError:
    try:
        from PyQt4.QtCore import Qt, QRectF, pyqtSignal, QT_VERSION_STR
        from PyQt4.QtGui import QGraphicsView, QGraphicsScene, QImage, QPixmap, QPainterPath, QFileDialog
    except ImportError:
        raise ImportError("QtImageViewer: Requires PyQt5 or PyQt4.")

#dpm -- added this import, Qt5 only
from PyQt5.QtCore import QPoint

__author__ = "Marcel Goldschen-Ohm <marcel.goldschen@gmail.com>"
__version__ = '0.9.0'


class QtImageViewer(QGraphicsView):
    """ PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.

    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).
    To display any other image format, you must first convert it to a QImage or QPixmap.

    Some useful image format conversion utilities:
        qimage2ndarray: NumPy ndarray <==> QImage    (https://github.com/hmeine/qimage2ndarray)
        ImageQt: PIL Image <==> QImage  (https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)

    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.
    """

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    leftMouseButtonPressed = pyqtSignal(float, float)
    rightMouseButtonPressed = pyqtSignal(float, float)
    leftMouseButtonReleased = pyqtSignal(float, float)
    rightMouseButtonReleased = pyqtSignal(float, float)
    leftMouseButtonDoubleClicked = pyqtSignal(float, float)
    rightMouseButtonDoubleClicked = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspectRatioMode = Qt.KeepAspectRatio

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = True

        self.resizeEvents = 0       # WJR
        self.drag_start_pos = None  # WJR

    def hasImage(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None

    def clearImage(self):
        """ Removes the current image pixmap from the scene if it exists.
        """
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")
        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))  # Set scene size to image size.
        self.updateViewer()

    def loadImageFromFile(self, fileName=""):
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if len(fileName) == 0:
            if QT_VERSION_STR[0] == '4':
                fileName = QFileDialog.getOpenFileName(self, "Open image file.")
            elif QT_VERSION_STR[0] == '5':
                fileName, dummy = QFileDialog.getOpenFileName(self, "Open image file.")
        if len(fileName) and os.path.isfile(fileName):
            image = QImage(fileName)
            self.setImage(image)

    def updateViewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            #self.fitInView(self.zoomStack[-1], Qt.IgnoreAspectRatio)  # Show zoomed rect (ignore aspect ratio).
            #dpm - changed to KeepAspect
            self.fitInView(self.zoomStack[-1], Qt.KeepAspectRatio)  # Show zoomed rect (KEEP aspect ratio).
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        self.resizeEvents += 1      # WJR
        print(self.resizeEvents)    # WJR
        self.updateViewer()

    #dpm these routines added to support zooming by wheel or comamnd
    #--------

    def getCurrentlyViewedSceneRectF(self):
        #dpm - added this routine
        #maybe a hack? to get the coords of the Viewport Scene that is currently showing in the zoomed and scrolled view
        #note that scene coords might be outside of the image itself - might need to intersect with image?
        scene_topleft = self.mapToScene(QPoint(1,1)) #get top left
        w = self.viewport().geometry().width()
        h = self.viewport().geometry().height() 
        
        scene_botright = self.mapToScene( QPoint(w,h) ) #get bottom right
        sceneRectF =  QRectF(scene_topleft, scene_botright )
        return sceneRectF    

    def zoom_in_out(self, direction, percent):
        #uses internal _zoom routine - see comments there
        #direction > 0 means zoom in, negatve means out
        #percent as a decimal fraction 0 - 1.0
        #practically, 0.05 seems good
        print(f'zoom_in_out: direction={direction}; percent ={percent}')
        sceneViewRF = self.getCurrentlyViewedSceneRectF()
        sceneViewIntesectRF = sceneViewRF.intersected(self.sceneRect())
        
        short_side = min(sceneViewIntesectRF.width(), sceneViewIntesectRF.height())
        inset = int(percent * short_side)
        self._doZoom(direction, inset)
        return

    #dpm - end of addded code
    #--------
    
    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            if self.canPan:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """
        QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())

            #dpm - added this code to update zoombox at end of mouse release so that 
            # we can come back to the scene as we left it.
            sceneViewRF = self.getCurrentlyViewedSceneRectF()
            sceneViewIntesectRF = sceneViewRF.intersected(self.sceneRect())
            self.zoomStack.append(sceneViewIntesectRF) 
            #dpm - end of added code

        elif event.button() == Qt.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QPainterPath())  # Clear current selection area.
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()
            self.setDragMode(QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

    def mouseDoubleClickEvent(self, event):
        """ Show entire image.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.zoomStack = []  # Clear zoom stack.
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mouseDoubleClickEvent(self, event)

    #-------------
    #dpm - added this code to handle wheel-based zooms and user-control based zooms
    #dpm - first the code that does the zoom

    def _doZoom(self, direction, inset):
        #direction > 0 means zoom in, direction < zero means zoom out
        #inset is the number of pixels to zoom in or out
        #inset should be positive, as direction determines in or out
        #assumes that inset value "makes sense" and that CanZoom has been checked

        sceneViewRF = self.getCurrentlyViewedSceneRectF()
        sceneViewIntesectRF = sceneViewRF.intersected(self.sceneRect())

        if direction > 0: #zooming in - by creating an inset selectionBBox
                       
            selectionBBox = sceneViewIntesectRF.adjusted(inset, inset, -2*inset, -2*inset)
            #print("wheelEvent - postive zoom in to be added to stack before call to updateViewer")
            if selectionBBox.isValid():
                self.zoomStack.clear()
                self.zoomStack.append(selectionBBox) #just a one deep "stack" to pass new scene view to fit to viewport
                self.updateViewer()
            else:
                print("doZoom: zoom IN - SELECTION BOX NOT VALID AT ", selectionBBox)
        
        else: #zoom out
            #print("wheelEvent - Negative zoom out to be added to stack before call to updateViewer")
            #zoom out by expanding from current Scene View (clipped to actual full scene, pointlessly on zoom out?)
            newRect = sceneViewIntesectRF.adjusted(-inset, -inset, 2*inset, 2*inset)
            newRectIntersected = newRect.intersected(self.sceneRect()) #sanitize
            self.zoomStack.clear()  #no longer using the stack - just pass new scene coords for "fit to"
            self.zoomStack.append(newRectIntersected)
            self.updateViewer()

    #dpm - the code to handle scroll wheel, and at least a few touchpads
    def wheelEvent(self, event):
        emsg = f'got wheel event: pos=({event.pos().x()},{event.pos().y()}), globalPos=({event.globalPos().x()}, '\
               f'{event.globalPos().y()}); '\
               f'pixelDelta(x,y) = ({event.pixelDelta().x()},{event.pixelDelta().y()}); ' \
               f'angleDelta(x,y) = ({event.angleDelta().x()},{event.angleDelta().y()})'
        print(emsg)
        if self.canZoom:
            
            jump = event.pixelDelta().y() #get the y value, at least on a mac!

            #dpm 6Nov2019 - added hack for (some?) windows trackpad which sends angleDelta but not pixelDelta????
            #give priority to pixelDelta, fall back to angleDelta if needed
            if jump == 0:
                #see if angleDelta can tell us the direction?
                jump = event.angleDelta().y()

                #we seem to get spurious Delta or Angle == 0 events with the trackpad?  if so, skip them
                if jump == 0:
                    event.accept()
                    return

            sceneViewRF = self.getCurrentlyViewedSceneRectF()
            sceneViewIntesectRF = sceneViewRF.intersected(self.sceneRect())
            
            short_side = min(sceneViewIntesectRF.width(), sceneViewIntesectRF.height())
            inset = 0.05 * short_side #ignore size of wheel movment - do 5% each time wheel moves at all
            
            #print("ON SCROLL sview = {} and intersected = {}".format(sceneViewRF, sceneViewIntesectRF))
            #print("WheelEvent: Inset calculated = ", inset)
            #jump will be positive or negative - all that matters
            self._doZoom(jump, inset)

        event.accept()
    
    #dpm - end of added code
    #--------------

if __name__ == '__main__':
    import sys
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        try:
            from PyQt4.QtGui import QApplication
        except ImportError:
            raise ImportError("QtImageViewer: Requires PyQt5 or PyQt4.")
    print('Using Qt ' + QT_VERSION_STR)

    def handleLeftClick(x, y):
        row = int(y)
        column = int(x)
        print("Clicked on image pixel (row="+str(row)+", column="+str(column)+")")

    #dpm quick test of zoom
    def test_zoom_in():
        #print("calling test zoom in")
        viewer.zoom_in_out(1, 0.20)
    def test_zoom_out():
        viewer.zoom_in_out(-1, 0.20)
    
    # Create the application.
    app = QApplication(sys.argv)

    # Create image viewer and load an image file to display.
    viewer = QtImageViewer()
    viewer.loadImageFromFile('/Users/Wes/Dropbox/Programming/ElectionTransparency/NewUI/NewUI_stacked/test_data/000000.jpg')  # Pops up file dialog.

    # Handle left mouse clicks with custom slot.
    viewer.leftMouseButtonPressed.connect(handleLeftClick)

    #dpm - test zoom - override left and right mouse click for test!
    # viewer.leftMouseButtonPressed.connect(test_zoom_in )
    # viewer.rightMouseButtonPressed.connect(test_zoom_out )


    # Show viewer and run application.
    viewer.show()
    sys.exit(app.exec_())
