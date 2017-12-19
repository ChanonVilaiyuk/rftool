# v.0.0.1 basic ui working

#Import python modules
import sys, os, re, getpass
import logging
moduleDir = os.path.dirname(sys.modules[__name__].__file__)

#Import maya commands
try:
    import maya.cmds as mc
    import maya.mel as mm
    import maya.OpenMayaUI as mui

    isMaya = True
except ImportError:
    isMaya = False
    packagePath = '%s/python/2.7/site-packages' % os.environ['RFSCRIPT']
    toolPath = '%s/core/maya' % os.environ['RFSCRIPT']
    corePath = '%s/core' % os.environ['RFSCRIPT']
    qtPath = '%s/lib/Qt.py' % os.environ['RFSCRIPT']
    appendPaths = [packagePath, toolPath, corePath, qtPath]

    # add PySide lib path
    for path in appendPaths:
        if not path in sys.path:
            sys.path.append(path)

    from startup import setEnv
    setEnv.set()

from rftool.utils import log_utils
from rftool.utils.ui import load

logFile = log_utils.name('test_tool', user=getpass.getuser())
logger = log_utils.init_logger(logFile)
logger.setLevel(logging.INFO)

os.environ['QT_PREFERRED_BINDING'] = os.pathsep.join(['PySide', 'PySide2'])
from Qt import wrapInstance, QtUiTools
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui
QtUiTools = QtUiTools()

def loadUI(uiPath, parent): 
    # read .ui directly
    dirname = os.path.dirname(uiPath)
    loader = QtUiTools.QUiLoader()
    loader.setWorkingDirectory(dirname)

    f = QtCore.QFile(uiPath)
    f.open(QtCore.QFile.ReadOnly)

    myWidget = loader.load(f, parent)

    f.close()
    return myWidget


# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)

logger.info('\n\n==============================================')

def show():
    if isMaya:
        logger.info('Run in Maya\n')
        uiName = 'TestUI'
        deleteUI(uiName)
        myApp = TestUI(getMayaWindow())
        # myApp.show()
        return myApp

    else:
        logger.info('Run in standalone\n')
        app = QtWidgets.QApplication.instance()
        if not app: 
            app = QtWidgets.QApplication(sys.argv)
        myApp = TestUI()
        # myApp.show()
        sys.exit(app.exec_())

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

class TestUI(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(TestUI, self).__init__(parent)
        # self.ui = ui.Ui_StillPublishUI()
        # self.ui.setupUi(self)
        uiFile = '%s/ui.ui' % moduleDir
        self.ui = load.loadUI(uiFile, self)
        self.ui.show()
        self.setWindowTitle('RF Still Publish v.0.0.1')