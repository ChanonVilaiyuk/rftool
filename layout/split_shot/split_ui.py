# v.0.0.1 basic ui working

#Import python modules
import sys, os, re, subprocess, inspect
import platform
import getpass
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
reload(log_utils)
from rftool.utils.ui import load

logFile = log_utils.name('split_tool', user=getpass.getuser())
logger = log_utils.init_logger(logFile)

 
from Qt import wrapInstance
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui
from Qt import _QtUiTools as QtUiTools
#Import GUI
# from PySide import QtCore
# from PySide import QtGui
# from PySide import QtUiTools
# import ui

from functools import partial

#import rftool commands
# from rftool import publish
from rftool.utils import file_utils
from rftool.utils import path_info
from rftool.utils import sg_wrapper
from rftool.utils import sg_process
from rftool.utils import icon
from rftool.utils.ui import combo_browser_widget
from rftool.utils.ui import pipeline_widget
from startup import config

module_path = sys.modules[__name__].__file__
module_dir  = os.path.dirname(module_path)

from rftool.layout.split_shot import split_shot_cmd
reload(split_shot_cmd)
reload(icon)

# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)

logger.info('\n\n==============================================')

def show():
    if isMaya:
        logger.info('Run in Maya\n')
        uiName = 'RfSplitUI'
        deleteUI(uiName)
        myApp = RFSplitSequence(getMayaWindow())
        return myApp

    else:
        logger.info('Run in standalone\n')
        app = QtWidgets.QApplication(sys.argv)
        myApp = RFSplitSequence()
        sys.exit(app.exec_())

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

class RFSplitSequence(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(RFSplitSequence, self).__init__(parent)
        # self.ui = ui.Ui_StillPublishUI()
        # self.ui.setupUi(self)
        uiFile = '%s/ui.ui' % moduleDir
        self.ui = load.loadUI(uiFile, self)
        self.ui.show()
        self.ui.setWindowTitle('RF Split Tool v.0.0.1')

        self.init_functions()
        self.init_signals()

    def init_functions(self): 
        self.list_shots()
        self.set_info()


    def init_signals(self): 
        self.ui.pushButton.clicked.connect(self.split_shots)
        self.ui.checkBox.stateChanged.connect(self.set_check_all)
        self.ui.listWidget.itemChanged.connect(self.set_info)


    def list_shots(self): 
        # list shot 
        shots = mc.ls(type='shot')

        for shot in shots: 
            iconPath = icon.camera
            item = QtWidgets.QListWidgetItem(self.ui.listWidget)
            checkable = True

            shotInfo = self.shot_info(shot)
            if not shotInfo: 
                iconPath = icon.cameraNa
                shotInfo = ('N/A') 
                checkable = False

            item.setText('%s - %s' % (shot, shotInfo))
            iconWidget = QtGui.QIcon()
            iconWidget.addPixmap(QtGui.QPixmap(iconPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(iconWidget)
            item.setData(QtCore.Qt.UserRole, shot)

            if checkable: 
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Checked)
            


    def set_info(self): 
        shots = self.get_check_state()

        if shots: 
            text = 'Split %s shots' % (len(shots))
        else: 
            text = 'Split 0 shot'

        self.ui.info_label.setText(text)

    def shot_info(self, shot): 
        startFrame = mc.getAttr('%s.startFrame' % shot)
        endFrame = mc.getAttr('%s.endFrame' % shot)
        sequenceStartFrame = mc.getAttr('%s.sequenceStartFrame' % shot)
        sequenceEndFrame = mc.getAttr('%s.sequenceEndFrame' % shot)

        if startFrame == sequenceStartFrame and endFrame == sequenceEndFrame: 
            duration = endFrame - startFrame + 1 

            return duration
        



    def set_check_all(self): 
        ''' set all shots checked ''' 
        items = [self.ui.listWidget.item(a) for a in range(self.ui.listWidget.count())]
        state = QtCore.Qt.Unchecked
        if self.ui.checkBox.isChecked(): 
            state = QtCore.Qt.Checked

        for item in items: 
            item.setCheckState(state)

        self.set_info()

    def get_check_state(self): 
        items = [self.ui.listWidget.item(a) for a in range(self.ui.listWidget.count())]
        checkedItems = [a for a in items if a.checkState() == QtCore.Qt.CheckState.Checked]

        if checkedItems: 
            return [a.data(QtCore.Qt.UserRole) for a in checkedItems]

    def split_shots(self): 
        shots = self.get_check_state()
        if shots: 
            result = QtWidgets.QMessageBox.question(self, 'Split sequences', 'Do you want to split %s shots? This will take several minutes.' % (len(shots)), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)

            if result == QtWidgets.QMessageBox.Ok: 
                split_shot_cmd.split_shots(shots=shots)
                QtWidgets.QMessageBox.information(self, 'Complete', 'Split %s shots complete' % len(shots))

        else: 
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Please select at lease 1 shot')

