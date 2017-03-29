# v.0.0.1 screen capture
# original source by Kun!!

#Import python modules
import sys, os, re, subprocess, inspect
import platform
import getpass

#Import maya commands
try:
    import maya.cmds as mc
    import maya.mel as mm
    import maya.OpenMayaUI as mui
    from shiboken import wrapInstance
    isMaya = True
except ImportError:
    isMaya = False
    packagePath = '%s/python/2.7/site-packages' % os.environ['RFSCRIPT']
    toolPath = '%s/core/maya' % os.environ['RFSCRIPT']
    corePath = '%s/core' % os.environ['RFSCRIPT']
    appendPaths = [packagePath, toolPath, corePath]

    # add PySide lib path
    for path in appendPaths:
        if not path in sys.path:
            sys.path.append(path)

    from startup import setEnv
    setEnv.set()

if isMaya:
	app = QtGui.QApplication.instance()
else:
	app = QtGui.QApplication(sys.argv)

from PySide import QtGui, QtCore
from PySide.QtGui import QPixmap, QApplication


class DimScreen(QtGui.QSplashScreen):
	""" darken the screen by making splashScreen """

	def __init__(self, w, h):
		""""""
		fillPix = QtGui.QPixmap(w, h)
		fillPix.fill(QtGui.QColor(1,1,1))
		super(DimScreen, self).__init__(fillPix)
		self.havePressed = False
		self.origin = QtCore.QPoint(0,0)
		self.end = QtCore.QPoint(0,0)
		self.rubberBand = None

		self.setWindowState(QtCore.Qt.WindowFullScreen)
		#self.setBackgroundRole(QtGui.QPalette.Dark)
		self.setWindowOpacity(0.4)

	def mousePressEvent(self, event):
		self.havePressed = True
		self.origin = event.pos()

		if not self.rubberBand:
			self.rubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
		self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
		self.rubberBand.show()

	def mouseMoveEvent(self, event):
		self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

	def mouseReleaseEvent(self, event):
		self.rubberBand.hide()
		if self.havePressed == True:
			self.end = event.pos()
			self.hide()

			QPixmap.grabWindow(QApplication.desktop().winId(), self.origin.x(), self.origin.y(), self.end.x()-self.origin.x(), self.end.y()-self.origin.y()).save('C:/Users/Ta/screenshot_windowed.png', 'png')


screenGeo = app.desktop().screenGeometry()
preCapScreen = DimScreen(screenGeo.width(), screenGeo.height())

def screenCap():
	""""""
	preCapScreen.show()

