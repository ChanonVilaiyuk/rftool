# v.0.0.2 Basic UI

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


from functools import partial
from startup import config
from rftool.utils import sg_process
from rftool.utils import get_config
from rftool.utils import file_utils
from rftool.utils import maya_utils
from rftool.utils import asm_utils
from rftool.utils import icon

from rftool.utils import log_utils
from rftool.utils.ui import load
import logging 

logFile = log_utils.name('asset_loader', user=getpass.getuser())
logger = log_utils.init_logger(logFile)

logger.setLevel(logging.INFO)


os.environ['QT_PREFERRED_BINDING'] = os.pathsep.join(['PySide', 'PySide2'])
from Qt import wrapInstance
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui


module_path = sys.modules[__name__].__file__
module_dir  = os.path.dirname(module_path)

import maya.OpenMayaUI as mui

# If inside Maya open Maya GUI
def getMayaWindow():
    """ maya instance windows """ 
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)


def show():
    if isMaya:
        logger.info('Run in Maya\n')
        uiName = 'assetLoaderUI'
        deleteUI(uiName)
        myApp = SGAssetLoader(getMayaWindow())
        # myApp.show()
        return myApp

    else:
        logger.info('Run in standalone\n')
        app = QtWidgets.QApplication.instance()
        if not app: 
            app = QtWidgets.QApplication(sys.argv)
        myApp = SGAssetLoader()
        # myApp.show()
        sys.exit(app.exec_())


def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

_iconpath = "C:/Users/vanef/Dropbox/script_server/icons/image_icon.png"

class SGAssetLoader(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(SGAssetLoader, self).__init__(parent)

        self.server = 'server'
        self.shotgun = 'shotgun'
        self.mode = self.server

        self.pathSep = '/'

        self.run_ui()
        self.initial_ui()
        self.load_data()
        self.init_connect()

    def run_ui(self):
        """ load ui """ 
        uiFile = '%s/app.ui' % moduleDir
        self.ui = load.loadUI(uiFile, self)
        self.ui.show()
        self.setWindowTitle('RF Asset Loader v.0.0.1')

    def initial_ui(self):
        self.rootPubl = os.getenv(config.RFPUBL)
        logger.info('Loader root has been set to %s' % self.rootPubl)

        self.set_project_combo()

        

    def init_connect(self):
        """ init signals """ 
        # radioButton 
        self.ui.shotgun_radioButton.clicked.connect(partial(self.set_mode, 'shotgun'))
    	self.ui.server_radioButton.clicked.connect(partial(self.set_mode, 'server'))

        self.ui.project_comboBox.currentIndexChanged.connect(self.project_trigger)

        # listWidget
        self.ui.typeAsset_listWidget.currentItemChanged.connect(self.list_subtype)

        # self.ui.typeAsset_listWidget.itemClicked.connect(self.list_thumbnail)
        # self.ui.subTypeAsset_listWidget.itemClicked.connect(self.list_thumbnail)

        # self.ui.size_comboBox.activated.connect(self.set_grid_size)
        # self.ui.thumbnail_listWidget.customContextMenuRequested.connect(self.actionMenu)


    def set_mode(self, mode): 
        self.mode = mode
        self.load_data()


    def set_project_combo(self):
        """ read project """ 
        lastSelected = mc.optionVar(q=config.projectVar)
        
        if self.mode == self.server: 
            # browse server 
            projects = file_utils.listFolder(self.rootPubl)

        self.ui.project_comboBox.addItems(projects)

        if lastSelected in projects: 
            self.ui.project_comboBox.setCurrentIndex(projects.index(lastSelected))



    def set_resolutions_combo(self):
        self.ui.lod_comboBox.clear()
        res_list = [{'proxy':'pr'},{'low':'lo'},{'medium':'md'},{'high':'hi'}]

        for index,res in enumerate(res_list):
            key = res.keys()[0]
            value = res.values()[0]

            self.ui.lod_comboBox.addItem(key.upper())
            self.ui.lod_comboBox.setItemData(index,value,QtCore.Qt.UserRole)

        self.ui.lod_comboBox.setCurrentIndex(2)


    def project_trigger(self): 
        """ project comboBox changed """ 
        project = str(self.ui.project_comboBox.currentText())
        mc.optionVar(sv=(config.projectVar, project))
        self.load_data()


    def set_level_combo(self):
        self.ui.level_comboBox.clear()
        level_list = ['model', 'rig', 'shade']

        for index,level in enumerate(level_list):

            self.ui.level_comboBox.addItem(level.upper())
            self.ui.level_comboBox.setItemData(index,level,QtCore.Qt.UserRole)

        self.ui.level_comboBox.setCurrentIndex(1)

    def get_asset_path(self):
        """ return browsing path """ 
        selProject = str(self.ui.project_comboBox.currentText())
        path = self.pathSep.join([self.rootPubl, selProject, config.asset])
        return path 
        # self.mode_path = self.rootPubl + '/' + prj_name + '/asset'

    def load_data(self):
        """ load data from server or shotgun """ 
        # browsePath = self.get_asset_path()
        
        # if self.ui.shotgun_radioButton.isChecked():
        #     self.types = sg_process.get_type()
        #     self.subtypes = sg_process.get_subtype()

        # if self.ui.server_radioButton.isChecked():
        #     self.types = get_config.allTypes(browsePath)
        #     self.subtypes = get_config.allSubtypes(browsePath)

        self.list_type()
        # self.list_subtype()

    def list_type(self):
        browsePath = self.get_asset_path()

        if self.mode == self.server: 
            assetTypes = get_config.allTypes(browsePath)

        if self.mode == self.shotgun: 
            assetTypes = sg_process.get_type()

        self.ui.typeAsset_listWidget.clear()
        filterType = str(self.ui.type_lineEdit.text())

        iconWidget = QtGui.QIcon()
        iconWidget.addPixmap(QtGui.QPixmap(icon.dir),QtGui.QIcon.Normal,QtGui.QIcon.Off)

        for typ in assetTypes:
            path = self.pathSep.join([browsePath, typ])
            item = QtWidgets.QListWidgetItem(self.ui.typeAsset_listWidget)
            item.setText(typ)
            item.setData(QtCore.Qt.UserRole, path)
            item.setIcon(iconWidget)

                # self.ui.typeAsset_listWidget.addItem(typ)

    def list_subtype(self):
        selTypeItem = self.ui.typeAsset_listWidget.currentItem()
        self.ui.subTypeAsset_listWidget.clear()

        if selTypeItem: 
            if self.mode == self.server: 
                path = selTypeItem.data(QtCore.Qt.UserRole)
                subtypes = file_utils.listFolder(path)

            if self.mode == self.shotgun: 
                subtypes = sg_process.get_subtype()
            
            # listSubtype 
            iconWidget = QtGui.QIcon()
            iconWidget.addPixmap(QtGui.QPixmap(icon.dir),QtGui.QIcon.Normal,QtGui.QIcon.Off)

            for sub in subtypes:
                subPath = self.pathSep.join([path, sub])
                item = QtWidgets.QListWidgetItem(self.ui.subTypeAsset_listWidget)
                item.setText(sub)
                item.setData(QtCore.Qt.UserRole, subPath)
                item.setIcon(iconWidget)


    def get_thumbnail(self,img_path):
        return file_utils.get_latest_file(img_path) 

    def load_asset(self):

        self.assets = dict()
        self.typ_name = None
        self.sub_name = None
        self.typ_path = None
        self.sub_path = None
        self.get_asset_path()

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