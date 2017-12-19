# v.0.0.1 first version
_version = 'v.0.0.1'
_description = 'wip'

#Import python modules
import sys, os, re, shutil, random
import subprocess

import logging
# logger = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler())

#Import GUI
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

from Qt import wrapInstance
from Qt import _QtUiTools

#Import maya commands
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as mui


# import ui
import ui
from rftool.utils import log_utils
from rftool.utils.ui import load
from rftool.fix.polytag import polytag_core
reload(polytag_core)

class Name: 
    ui = 'AssetSwitchUI'
    logname = 'AssetSwitchPolyTag'
    title = 'Asset Switch UI'

moduleDir = os.path.dirname(sys.modules[__name__].__file__)
user = os.environ.get('RFUSER', 'unknown')

logFile = log_utils.name(Name.logname, user=user)
logger = log_utils.init_logger(logFile)
logger.setLevel(logging.INFO)



# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)
    # return sip.wrapinstance(long(ptr), QObject)


def show():
    deleteUI(Name.ui)
    myApp = SGFileManager(getMayaWindow())
    # myApp.ui.show()
    return myApp

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

class Library: 
    levelMap = ['model_pr', 'model_md', 'rig_pr', 'rig_md', 'gpu_pr', 'gpu_md', 'ren_md', 'rsproxy_md']


class SGFileManager(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        self.count = 0
        #Setup Window
        super(SGFileManager, self).__init__(parent)
        # self.ui = ui.Ui_SGFileManagerUI()
        uiFile = '%s/ui.ui' % moduleDir
        self.ui = load.loadUIMaya(uiFile, self)
        self.ui.show()
        # self.ui.setupUi(self)
        # self.ui.show()
        self.ui.setWindowTitle('%s %s - %s' % (Name.title, _version, _description))

        self.list_ui()
        self.init_signals()


    def list_ui(self): 
        """ list asset on the ui """ 
        info = polytag_core.list_polytag()
        self.ui.asset_listWidget.clear()

        for assetName, data in sorted(info.iteritems()): 
            item = QtWidgets.QListWidgetItem(self.ui.asset_listWidget)
            item.setData(QtCore.Qt.UserRole, data)
            item.setText(assetName)
            # self.ui.asset_listWidget.addItem(assetName)

        self.list_lib()


    def list_lib(self): 
        self.ui.lib_listWidget.clear()

        for level in Library.levelMap: 
            self.ui.lib_listWidget.addItem(level)


    def init_signals(self): 
        # list widget 
        self.ui.asset_listWidget.itemSelectionChanged.connect(self.list_polys)
        self.ui.switch_pushButton.clicked.connect(self.switch)

    def list_polys(self): 
        self.list_poly_ui()

        if self.ui.select_checkBox.isChecked(): 
            items = [self.ui.ply_listWidget.item(a) for a in range(self.ui.ply_listWidget.count())]
            plys = [a.data(QtCore.Qt.UserRole) for a in items]
            mc.select(plys)

    def list_poly_ui(self): 
        """ list asset members """ 
        self.ui.ply_listWidget.clear()
        selItems = self.ui.asset_listWidget.selectedItems()

        if selItems: 
            for assetItem in selItems: 
                asset, plys = assetItem.data(QtCore.Qt.UserRole)

                for ply in plys: 
                    shortName = ply.split('|')[-1]
                    item = QtWidgets.QListWidgetItem(self.ui.ply_listWidget)
                    item.setText(shortName)
                    item.setData(QtCore.Qt.UserRole, ply)


    def switch(self): 
        plys = mc.ls(sl=True)

        if self.ui.lib_listWidget.currentItem(): 
            level = str(self.ui.lib_listWidget.currentItem().text())
            polytag_core.switch_selection(level)


