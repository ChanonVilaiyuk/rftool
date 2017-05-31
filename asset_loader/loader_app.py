#Import python modules
import sys, os, re, shutil, random

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

#Import GUI
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

# print type(QtCore)
# from QtCore import *
# from QtWidgets import *
# from QtGui import *

from Qt import wrapInstance
from Qt import _QtUiTools

from startup import config
from rftool.utils import sg_process
from rftool.utils import get_config
from rftool.utils import file_utils
from rftool.utils import maya_utils
from rftool.utils import asm_utils

#Import maya commands
import maya.cmds as mc
import maya.mel as mm
from functools import partial

module_path = sys.modules[__name__].__file__
module_dir  = os.path.dirname(module_path)

import maya.OpenMayaUI as mui

# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)
    # return sip.wrapinstance(long(ptr), QObject)

def show():
    uiName = 'assetLoaderUI'
    deleteUI(uiName)
    myApp = SGAssetLoader(getMayaWindow())
    
    myApp.ui.project_comboBox.setCurrentIndex(21)
    myApp.load_data()
    myApp.ui.typeAsset_listWidget.setCurrentRow(1)

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

_iconpath = "C:/Users/vanef/Dropbox/script_server/icons/image_icon.png"

class SGAssetLoader(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(SGAssetLoader, self).__init__(parent)

        self.run_ui()
        self.initial_ui()
        self.init_connect()

    def run_ui(self):
        loader = _QtUiTools.QUiLoader()
        file = QtCore.QFile(module_dir + "/app.ui")
        file.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.ui.show()

    def initial_ui(self):

        self.rootPubl = os.getenv(config.RFPUBL)

        self.set_project_combo()
        self.set_level_combo()
        self.set_resolutions_combo()

    def init_connect(self):
    	self.ui.download_pushButton.clicked.connect(self.load_data)
        self.ui.typeAsset_listWidget.itemClicked.connect(self.list_thumbnail)
        self.ui.subTypeAsset_listWidget.itemClicked.connect(self.list_thumbnail)

        self.ui.size_comboBox.activated.connect(self.set_grid_size)
        self.ui.thumbnail_listWidget.customContextMenuRequested.connect(self.actionMenu)

    def set_project_combo(self):
        self.projects = get_config.getProjectNames()
        #self.projects = ['AAA Game Template', 'Audio Template', 'Demo: Animation', 'Demo: Cinematic Project', 'Double_Monkey', 'ELEX Trailer', 'FOW', 'FOW:RAMAYANA', 'Film Template', 'GARUDA', 'Game Cinematic Template', 'Kaan Project', 'Kaan Template', 'Mobile Game Template', 'Motion Capture Template', 'Poul Test', 'Shotgun_Test', 'TV Series Template', 'Template Project', 'Two_Heroes', 'ZILA 2016', 'project']
        
        self.ui.project_comboBox.addItems(self.projects)

    def set_resolutions_combo(self):
        self.ui.lod_comboBox.clear()
        res_list = [{'proxy':'pr'},{'low':'lo'},{'medium':'md'},{'high':'hi'}]

        for index,res in enumerate(res_list):
            key = res.keys()[0]
            value = res.values()[0]

            self.ui.lod_comboBox.addItem(key.upper())
            self.ui.lod_comboBox.setItemData(index,value,QtCore.Qt.UserRole)

        self.ui.lod_comboBox.setCurrentIndex(2)

    def set_level_combo(self):
        self.ui.level_comboBox.clear()
        level_list = ['model', 'rig', 'shade']

        for index,level in enumerate(level_list):

            self.ui.level_comboBox.addItem(level.upper())
            self.ui.level_comboBox.setItemData(index,level,QtCore.Qt.UserRole)

        self.ui.level_comboBox.setCurrentIndex(1)

    def get_mode_path(self):
        prj_name = str(self.ui.project_comboBox.currentText())
        self.mode_path = self.rootPubl + '/' + prj_name + '/asset'

    def load_data(self):

        self.get_mode_path()
        
        if self.ui.shotgun_radioButton.isChecked():
            self.types = sg_process.get_type()
            self.subtypes = sg_process.get_subtype()
        if self.ui.server_radioButton.isChecked():
            self.types = get_config.allTypes(self.mode_path)
            self.subtypes = get_config.allSubtypes(self.mode_path)

        self.list_type()
        self.list_subtype()

    def list_type(self):
        self.ui.typeAsset_listWidget.clear()
        typ_name = str(self.ui.type_lineEdit.text())

        for typ in self.types:
            if typ_name.lower() in typ.lower():
                self.ui.typeAsset_listWidget.addItem(typ)

    def list_subtype(self):
        self.ui.subTypeAsset_listWidget.clear()
        sub_name = str(self.ui.subtype_lineEdit.text())

        for sub in self.subtypes:
            if sub_name.lower() in sub.lower():
                self.ui.subTypeAsset_listWidget.addItem(sub)

    def get_thumbnail(self,img_path):
        return file_utils.get_latest_file(img_path) 

    def load_asset(self):

        self.assets = dict()
        self.typ_name = None
        self.sub_name = None
        self.typ_path = None
        self.sub_path = None
        self.get_mode_path()

        try:
            self.typ_name = self.ui.typeAsset_listWidget.currentItem().text()
            self.sub_name = self.ui.subTypeAsset_listWidget.currentItem().text()
        except AttributeError as attrExc:
            pass

        # get type and subtype path
        if self.typ_name:
            self.typ_path = self.mode_path + '/' + self.typ_name

        if self.sub_name:
            self.sub_path = self.typ_path + '/' + self.sub_name

        # get asset lists  
        if self.typ_path and os.path.exists(self.typ_path):
            for index,sub in enumerate(self.subtypes):
                path = self.typ_path + '/' + sub
                if os.path.exists(path) and sub == self.sub_name:

                    for name in file_utils.listFolder(path):
                        #asset_path = path + '/' + name
                        img_path = path + '/' + name + '/images'
                        lib_path = path + '/' + name + '/lib'

                        self.assets[name] = { 'image' : self.get_thumbnail(img_path), 'lib' : lib_path }
        if self.sub_path and os.path.exists(self.sub_path):
            for name in file_utils.listFolder(path):
                #asset_path = path + '/' + name
                img_path = path + '/' + name + '/images'
                lib_path = path + '/' + name + '/lib'

                self.assets[name] = { 'image' : self.get_thumbnail(img_path), 'lib' : lib_path }

    def set_grid_size(self):
        # set grid size
        size_text = str(self.ui.size_comboBox.currentText())
        self.size_num  = int(size_text.split('*')[0])

        grid_size = QtCore.QSize(self.size_num,self.size_num+10)
        icon_size = QtCore.QSize(self.size_num,self.size_num)

        self.ui.thumbnail_listWidget.setGridSize(grid_size)
        self.ui.thumbnail_listWidget.setIconSize(icon_size)

    def list_thumbnail(self):
        self.ui.thumbnail_listWidget.clear()
        self.set_grid_size()
        self.load_asset()

        search_name = str(self.ui.search_lineEdit.text())

        if self.assets:
            for name in sorted(self.assets.keys()):
                # print name, self.assets[name]
                if search_name.lower() in name.lower():
                    icon = QtGui.QIcon(self.assets[name]['image'])
                    item = QtWidgets.QListWidgetItem(self.ui.thumbnail_listWidget)
                    item.setIcon(icon)
                    # item.setIconSize()
                    item.setText(name)
        else:
            self.ui.thumbnail_listWidget.addItem('No Asset.')

    def actionMenu(self,event):

        ref_menu = QtWidgets.QMenu(self.ui.thumbnail_listWidget)

        item = self.ui.thumbnail_listWidget.currentItem()
        asset_name = item.text()

        lib_dir = self.assets[asset_name]['lib']
        lib_files = file_utils.listFile(lib_dir)

        default_action = QtWidgets.QAction('create reference (default)',self.ui.thumbnail_listWidget)
        create_menu = QtWidgets.QMenu('create reference...',self.ui.thumbnail_listWidget)
        import_menu = QtWidgets.QMenu('import reference...',self.ui.thumbnail_listWidget)
        open_menu = QtWidgets.QMenu('open file...',self.ui.thumbnail_listWidget)
        asm_action = QtWidgets.QAction('create assembly',self.ui.thumbnail_listWidget)

        for lib in lib_files:
            if '.ma' in lib and not 'ad' in lib:
                create_action = QtWidgets.QAction('create %s' %lib, self.ui.thumbnail_listWidget)
                import_action = QtWidgets.QAction('import %s' %lib, self.ui.thumbnail_listWidget)
                open_action = QtWidgets.QAction('open %s' %lib, self.ui.thumbnail_listWidget)
                create_menu.addAction(create_action)
                import_menu.addAction(import_action)
                open_menu.addAction(open_action)

        ref_menu.addAction(default_action)
        ref_menu.addSeparator()
        ref_menu.addMenu(create_menu)
        ref_menu.addMenu(import_menu)
        ref_menu.addMenu(open_menu)
        ref_menu.addAction(asm_action)

        ref_menu.popup(self.ui.thumbnail_listWidget.mapToGlobal(event))
        result = ref_menu.exec_(self.ui.thumbnail_listWidget.mapToGlobal(event))

        if result:
            self.checkAction(result.text())

    def checkAction(self,result):
        
        item = self.ui.thumbnail_listWidget.currentItem()
        asset_name = item.text()

        res_index = self.ui.lod_comboBox.currentIndex()
        res = self.ui.lod_comboBox.itemData(res_index,QtCore.Qt.UserRole)

        level_index = self.ui.level_comboBox.currentIndex()
        level = self.ui.level_comboBox.itemData(level_index,QtCore.Qt.UserRole)

        lib_dir = self.assets[asset_name]['lib']

        if result == 'create reference (default)':

            for lib in file_utils.listFile(lib_dir):
                if level in lib and res in lib:
                    lib_path = lib_dir + '/' + lib
                    break

            maya_utils.create_reference(asset_name, lib_path)

        if 'create' in result and '.ma' in result:
            file_name = result.split('create ')[-1]
            lib_path = lib_dir + '/' + file_name

            maya_utils.create_reference(asset_name, lib_path)

        if 'import' in result and '.ma' in result:
            file_name = result.split('import ')[-1]
            lib_path = lib_dir + '/' + file_name

            maya_utils.import_file(asset_name, lib_path)

        if 'open' in result and '.ma' in result:
            file_name = result.split('open ')[-1]
            lib_path = lib_dir + '/' + file_name

            maya_utils.open_file(lib_path)

        if result == 'create assembly':

            for lib in file_utils.listFile(lib_dir):
                if 'ad' in lib:
                    lib_path = lib_dir + '/' + lib
                    break
                    
            if lib_path:
                ar_node = maya_utils.create_asm_reference(asset_name,lib_path)

                for rep in asm_utils.listRepIndex(ar_node):
                    if res in rep:
                        asm_utils.setActiveRep(ar_node,rep)
                        break