import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QPixmap, QApplication

app = QApplication(sys.argv)

myForm = QtGui.QMainWindow()
myForm.centralwidget = QtGui.QWidget(myForm)
myForm.centralwidget.setObjectName("centralwidget")

class fakeWindow(QtGui.QSplashScreen):

	def __init__(self, w, h):
		""""""
		fillPix = QtGui.QPixmap(w, h)
		fillPix.fill(QtGui.QColor(1,1,1))
		super(fakeWindow, self).__init__(fillPix)
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

			QPixmap.grabWindow(QApplication.desktop().winId(), self.origin.x(), self.origin.y(), self.end.x()-self.origin.x(), self.end.y()-self.origin.y()).save('screenshot_windowed.jpg', 'jpg')

screenGeo = app.desktop().screenGeometry()
fakeOne = fakeWindow(screenGeo.width(), screenGeo.height())
#fakeOne.centralwidget = QtGui.QWidget(myForm)
#fakeOne.centralwidget.setObjectName("centralwidget")
#fakeOne.setCentralWidget = fakeOne.centralwidget 
#fakeOne.show()

def screenCap():
	""""""
	fakeOne.show()

btn_screenCap = QtGui.QPushButton(myForm.centralwidget)
btn_screenCap.clicked.connect(screenCap)
btn_screenCap.setText('Got Cha!!')

myForm.setCentralWidget(btn_screenCap)
myForm.show()



sys.exit(app.exec_())