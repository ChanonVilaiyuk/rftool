# This is UI template that can run both pyside and pyside2 and pyside standalone
import sys, os 
import logging
logger = logging.getLogger()

moduleFile = sys.modules[__name__].__file__
moduleDir = os.path.dirname(moduleFile)

try: 
    import maya.cmds as mc
    import maya.mel as mm 
    import maya.OpenMayaUI as mui
    isMaya = True

except ImportError: 
    sys.path.append('D:/Dropbox/script_server/python/2.7/site-packages')
    sys.path.append('D:/Dropbox/script_server/lib/Qt.py-master')
    isMaya = False

# import Qt
os.environ['QT_PREFERRED_BINDING'] = os.pathsep.join(['PySide', 'PySide2'])
from Qt import QtGui
from Qt import QtWidgets
from Qt import QtCore
from Qt import QtUiTools
from Qt import wrapInstance
from Qt import QtCompat
QtUiTools = QtUiTools()

# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)

def show():
    if isMaya:
        logger.info('Run in Maya\n')
        uiName = 'MainWindow'
        deleteUI(uiName)
        myApp = MyForm(getMayaWindow())
        return myApp

    else:
        logger.info('Run in standalone\n')
        app = QtWidgets.QApplication(sys.argv)
        myApp = MyForm()
        sys.exit(app.exec_())

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

def loadUI(uiPath, parent): 
    # read .ui directly
    dirname = os.path.dirname(uiPath)
    ui = QtCompat.loadUi(uiPath)
    return ui
    # loader = QtUiTools.QUiLoader()
    # loader.setWorkingDirectory(dirname)

    # f = QtCore.QFile(uiPath)
    # f.open(QtCore.QFile.ReadOnly)

    # myWidget = loader.load(f, parent)

    # f.close()
    # return myWidget


class MyForm(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        self.count = 0
        #Setup Window
        super(MyForm, self).__init__(parent)

        uiFile = '%s/ui.ui' % moduleDir
        self.ui = loadUI(uiFile, self)
        self.ui.show()

""" for standalone run this """
if __name__ == '__main__':
    show()