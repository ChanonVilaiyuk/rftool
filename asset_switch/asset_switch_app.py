# v.0.0.1 library wip
_title = 'RF Asset Switch'
_version = 'v.0.0.1'
_des = 'beta'
uiName = 'RFAssetSwitch'

#Import python modules
import sys
import os 
import logging
import getpass
import json

moduleDir = os.path.dirname(sys.modules[__name__].__file__)
appName = os.path.splitext(os.path.basename(sys.modules[__name__].__file__))[0]

import maya.cmds as mc 
import maya.mel as mm 
import maya.OpenMayaUI as mui

# initial env setup 
user = '%s-%s' % (os.environ.get('RFUSER'), getpass.getuser())

from rf.utils import log_utils

# set logger
logFile = log_utils.name(appName, user=user)
logger = log_utils.init_logger(logFile)
logger.setLevel(logging.INFO)

from rf.utils import load
from rf.utils import file_utils
from rftool.utils import maya_utils

os.environ['QT_PREFERRED_BINDING'] = os.pathsep.join(['PySide', 'PySide2'])
from Qt import wrapInstance
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui


# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)

logger.info('Running RFSCRIPT from %s' % os.environ.get('RFSCRIPT'))
logger.info('\n\n==============================================')

class Config: 
    path = 'app_config.json'
    data = file_utils.json_loader('%s/%s' % (moduleDir, path))


class Color: 
    green = [0, 200, 0]
    red = [200, 0, 0]
    grey = [100, 100, 100]


class RFAssetSwitch(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(RFAssetSwitch, self).__init__(parent)

        # ui read
        uiFile = '%s/ui.ui' % moduleDir
        self.ui = load.setup_ui_maya(uiFile, self)
        self.ui.show()
        self.ui.setWindowTitle('%s %s - %s' % (_title, _version, _des))


        self.set_app_ui()
        self.init_signals()


    def set_app_ui(self): 
        # list refs 
        self.list_refs()
        self.list_res()


    def init_signals(self): 
        self.ui.refresh_pushButton.clicked.connect(self.list_refs)
        self.ui.switch_pushButton.clicked.connect(self.switch_asset)


    def list_refs(self): 
        """ list reference widget """
        paths = mc.file(q=True, r=True)
        rnNodes = [mc.referenceQuery(a, referenceNode=True) for a in paths]

        self.ui.asset_listWidget.clear()

        if rnNodes: 
            for rnNode in rnNodes: 
                path = mc.referenceQuery(rnNode, f=True)
                # widget display secton 
                project = self.get_project(path)
                res = Config.data.get(project, dict()).get('res')

                widget = RefListWidgetItem(items=len(res))
                item = QtWidgets.QListWidgetItem(self.ui.asset_listWidget)
                data = self.set_display_info(widget, rnNode, item)

                item.setSizeHint(widget.sizeHint())
                self.ui.asset_listWidget.setItemWidget(item, widget)



    def switch_asset(self): 
        """ switch reference signals """ 
        items = self.ui.asset_listWidget.selectedItems()
        targetRes = str(self.ui.res_comboBox.currentText())

        if items: 
            for item in items: 
                data = item.data(QtCore.Qt.UserRole)
                switchPath = data.get(targetRes)
                rnNode = data.get('current')
                currentPath = mc.referenceQuery(rnNode, f=True)

                if os.path.exists(switchPath): 
                    # run switch 
                    logger.info('Switching reference %s ...' % rnNode)
                    logger.debug(currentPath)
                    logger.debug(switchPath)
                    try: 
                        maya_utils.replace_reference(currentPath, switchPath)
                    except Exception as e: 
                        logger.error(e)
                        logger.info('Error during switch reference %s' % rnNode)
                
                    # update ui
                    widget = self.ui.asset_listWidget.itemWidget(item)
                    self.set_display_info(widget, rnNode, item)
                    logger.info('Success')

                else: 
                    QtWidgets.QMessageBox.warning(self, 'Warning', 'Path not exists %s' % switchPath)
                    logger.warning('Switch target path does not exists %s' % switchPath)



    def set_display_info(self, widget, rnNode, item): 
        data = dict()
        data.update({'current': rnNode})
        path = mc.referenceQuery(rnNode, f=True)
        
        project = self.get_project(path)
        
        # get config 
        # ani, ldv 
        res = Config.data.get(project, dict()).get('res')
        # level to split res 
        levelRes = Config.data.get(project, dict()).get('level')
        # get type level 
        typeLevel = Config.data.get(project, dict()).get('typeLevel')
        
        # display name 
        namespace = self.get_namespace(path)
        
        # current file res 
        currentRes = self.get_res(path, levelRes)
        assetType = self.get_type(path, typeLevel)

        # set name 
        widget.set_main_item(namespace)
        widget.set_second_item(assetType)

        for i in range(len(res)): 
            widget.set_item(i, res[i])
            replaceFile = self.get_res_file(path, res[i], levelRes)
            color = get_color(os.path.exists(replaceFile))

            widget.set_item_color(i, color)
            data.update({res[i]: replaceFile})

            # set current res 
            if currentRes == res[i]: 
                widget.set_item_bold(i, True)
                widget.set_item_color(i, Color.green)

        item.setData(QtCore.Qt.UserRole, data)



    def list_res(self): 
        sn = mc.file(q=True, sn=True)

        if sn: 
            project = self.get_project(sn)
            res = Config.data.get(project, dict()).get('res')
            self.ui.res_comboBox.addItems(res)


    def get_project(self, path): 
        return os.path.splitdrive(path)[-1].split('/')[1]


    def get_namespace(self, path): 
        rnNode = mc.referenceQuery(path, referenceNode=True)
        namespace = mc.referenceQuery(rnNode, namespace=True)
        return namespace.replace(':', '')

    def get_res(self, path, levelRes): 
        basename = os.path.basename(path)
        level = os.path.splitext(basename)[0].split('_')[levelRes]
        return level

    def get_type(self, path, levelType): 
        level = os.path.splitext(path)[0].split('/')[levelType]
        return level


    def get_res_file(self, path, res, levelRes): 
        basename = os.path.basename(path).split('{')[0]
        currentRes = '_%s' % self.get_res(path, levelRes)
        newRes = '_%s' % res
        newName = basename.replace(currentRes, newRes)
        newResPath = '%s/%s' % (os.path.dirname(path), newName)

        return newResPath


def get_color(status): 
    if status: 
        return Color.grey
    else: 
        return Color.red

        

def show(): 
    deleteUI(uiName)
    app = RFAssetSwitch(getMayaWindow())
    return app

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)


class RefListWidgetItem(QtWidgets.QWidget) :
    def __init__(self, items=2, parent = None) :
        super(RefListWidgetItem, self).__init__(parent)
        # set label
        self.allLayout = QtWidgets.QHBoxLayout()
        self.textLabel1 = QtWidgets.QLabel()
        self.textLabel2 = QtWidgets.QLabel()
        self.textLabels = []

        # self.descriptionLabel = QtWidgets.QLabel()
        # self.descriptionLabel.setStyleSheet('color: rgb(%s, %s, %s);' % (100, 100, 100))

        # set icon
        self.iconQLabel = QtWidgets.QLabel()

        self.spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.allLayout.addWidget(self.iconQLabel, 1, 0)
        self.allLayout.addWidget(self.textLabel1, 9, 1)
        self.allLayout.addWidget(self.textLabel2, 0, 2)
        self.allLayout.addItem(self.spacerItem)

        for i in range(items): 
            self.textLabels.append(QtWidgets.QLabel())
            self.allLayout.addWidget(self.textLabels[i], 3, i+3)


        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

        # self.descriptionLabel.setFont(font)

    def set_main_item(self, text): 
        self.textLabel1.setText(text)

    def set_second_item(self, text): 
        self.textLabel2.setText(text)

    def set_item(self, index, text): 
        self.textLabels[index].setText(text)

    def set_item_color(self, index, color): 
        self.textLabels[index].setStyleSheet('color: rgb(%s, %s, %s);' % (color[0], color[1], color[2]))

    def set_item_bold(self, index, bold): 
        # set font 
        font = QtGui.QFont()
        # font.setPointSize(9)
        font.setBold(bold)
        self.textLabels[index].setFont(font)

