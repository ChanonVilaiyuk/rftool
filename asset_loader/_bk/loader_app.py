#Import python modules
import sys, os, re, shutil, random

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

#Import GUI
from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools

from shiboken import wrapInstance

#Import maya commands
import maya.cmds as mc
import maya.mel as mm
from functools import partial

# # import ui
# import ui
from rftool.utils import file_utils
from rftool.utils import path_info
from rftool.utils import sg_wrapper
from rftool.utils import sg_process
from startup import config
# from rftool.utils.userCheck import ui_dialog

module_path = sys.modules[__name__].__file__
module_dir  = os.path.dirname(module_path)

import maya.OpenMayaUI as mui

# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtGui.QWidget)
    # return sip.wrapinstance(long(ptr), QObject)

def show():
    uiName = 'assetLibUI'
    deleteUI(uiName)
    myApp = SGAssetLoader(getMayaWindow())
    # myApp.show()

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

def get_project():
    sg_project = dict()

    for i in sg_wrapper.get_projects():
        project_name = i['name']
        sg_project[project_name] = i

    return sg_project

class SGAssetLoader(QtGui.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(SGAssetLoader, self).__init__(parent)

        self.run_ui()
        self.initial_ui()
        self.init_connect()

    def run_ui(self):
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(module_dir + "/ui.ui")
        file.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()

        self.ui.show()

    def init_connect(self):
        self.ui.project_comboBox.activated.connect(self.get_asset)
        self.ui.download_pushButton.clicked.connect(self.sg_get_entitys_thumbnail)
        self.ui.typeAsset_listWidget.itemSelectionChanged.connect(self.selected_type_list)
        self.ui.subTypeAsset_listWidget.itemSelectionChanged.connect(self.select_sub_list)
        # self.ui.asset_listWidget.itemSelectionChanged.connect(self.select_asset_list)

    def initial_ui(self):
        self.list_project()
        self.get_asset()

    def list_project(self):
        # self.ui.project_comboBox.addItems(get_project().keys())
        self.ui.project_comboBox.addItems(['project'])

    # def set_asset_path(self):

    def get_asset(self):

        asset_types = []
        asset_subtypes = []
        asset_names = []

        project_name = str(self.ui.project_comboBox.currentText())
        self.sg_assets = sg_process.get_assets(project_name)

        for i in self.sg_assets:
            if not i['sg_asset_type'] in asset_types:
                asset_types.append(i['sg_asset_type'])
            if not i['sg_subtype'] in asset_subtypes:
                asset_subtypes.append(i['sg_subtype'])
            if not i['code'] in asset_names:
                asset_names.append(i['code'])

        lists_asset_types     = self.list_sorted(asset_types)
        lists_asset_subtypes  = self.list_sorted(asset_subtypes)
        lists_asset_names     = self.list_sorted(asset_names,False)

        self.ui.typeAsset_listWidget.addItems(lists_asset_types)
        self.ui.subTypeAsset_listWidget.addItems(lists_asset_subtypes)
        self.ui.asset_listWidget.addItems(lists_asset_names)

    def list_sorted(self, lists, asset_check=True):
        none_check = False

        if lists:
            if None in lists:
                lists.remove(None)
                none_check = True

            lists = sorted(lists, key=str.lower)

            if none_check :
                lists.insert(0, '(Blank)')

            if asset_check :
                lists.insert(0, 'All')

        return lists

    def selected_type_list(self):
        type_name = 'All'
        sub_name = 'All'
        asset_name = 'All'
        
        if self.ui.typeAsset_listWidget.currentItem():
            self.ui.subTypeAsset_listWidget.clear()
            self.ui.asset_listWidget.clear()
            type_item = self.ui.typeAsset_listWidget.currentItem()
            type_name = str(type_item.text())

        self.selected_all_list(type_name,sub_name,asset_name)

    def select_sub_list(self):
        type_item = self.ui.typeAsset_listWidget.currentItem()
        type_name = str(type_item.text())

        sub_name = 'All'
        asset_name = 'All'

        if self.ui.subTypeAsset_listWidget.currentItem():
            sub_item = self.ui.subTypeAsset_listWidget.currentItem()
            sub_name = str(sub_item.text())
            self.ui.asset_listWidget.clear()

        self.selected_all_list(type_name,sub_name,asset_name)

    # def select_asset_list(self):
    #     type_item = self.ui.typeAsset_listWidget.currentItem()
    #     type_name = str(type_item.text())
    #     sub_item = self.ui.subTypeAsset_listWidget.currentItem()
    #     sub_name = str(sub_item.text())

    #     asset_name = 'All'

    #     if self.ui.asset_listWidget.currentItem():
    #         asset_item = self.ui.asset_listWidget.currentItem()
    #         asset_name = str(asset_item.text())

    #     self.selected_all_list(type_name,sub_name,asset_name)


    def selected_all_list(self, type_name ='All',subtype_name='All',asset_name='All'):

        lists_asset_subtypes = []
        lists_asset_names = []

        for i in self.sg_assets:

            if (type_name == i['sg_asset_type']) or (type_name == '(Blank)' and i['sg_asset_type'] == None):
                
                if not i['sg_subtype'] in lists_asset_subtypes:
                    lists_asset_subtypes.append(i['sg_subtype'])

                if subtype_name == i['sg_subtype']:
                    lists_asset_names.append(i['code'])

                if subtype_name == 'All':
                    lists_asset_names.append(i['code'])

            if type_name == 'All':
                lists_asset_subtypes.append(i['sg_subtype'])
                lists_asset_names.append(i['code'])

        if subtype_name == 'All' and not self.ui.subTypeAsset_listWidget.currentItem():
            lists_asset_subtypes = self.list_sorted(lists_asset_subtypes)
            self.ui.subTypeAsset_listWidget.addItems(lists_asset_subtypes)

        if asset_name == 'All':
            lists_asset_names = self.list_sorted(lists_asset_names,False)
            self.ui.asset_listWidget.addItems(lists_asset_names)

    def sg_get_entitys_thumbnail(self, entitys):
        entitys = self.sg_assets
        # entity with ['image','code'] fields.
        tmp_icon = '$RFSCRIPT/icon/tmp_thumbnail.jpg'
        
        for i in entitys:

            icon_dir = '$RFSCRIPT/icon/_sg/thumbnail'
            if not os.path.exists(icon_dir):
                os.makedirs(icon_dir)

            icon_path = icon_dir + '/' + i['code'] + '.jpg'

            if not i['image'] == None:
                url_utils.download_from_url(i['image'],icon_path)
            else:
                shutil.copy(tmp_icon,icon_path)

            i['image'] = icon_path
            print '- Download thumbnail : ' + icon_path

        return entitys