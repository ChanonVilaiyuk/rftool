# v.0.0.1 basic ui working

#Import python modules
import sys, os, re, subprocess, inspect
from collections import OrderedDict
import logging 
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
from rftool.utils.ui import load
from rftool.utils import path_info
from rftool.utils import maya_utils
from rftool.utils import pipeline_utils

logFile = log_utils.name('asset_mover', user=getpass.getuser())
logger = log_utils.init_logger(logFile)
logger.setLevel(logging.DEBUG)

#Import GUI
os.environ['QT_PREFERRED_BINDING'] = os.pathsep.join(['PySide', 'PySide2'])
from Qt import wrapInstance
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui
from Qt import _QtUiTools as QtUiTools

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
from rftool.utils.ui import ui_wrapper
from startup import config

module_path = sys.modules[__name__].__file__
module_dir  = os.path.dirname(module_path)


# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)

logger.info('\n\n==============================================')

def show():
    if isMaya:
        logger.info('Run in Maya\n')
        uiName = 'AssetMoverUI'
        deleteUI(uiName)
        myApp = AssetMoverUI(getMayaWindow())
        return myApp

    else:
        logger.info('Run in standalone\n')
        app = QtWidgets.QApplication.instance()
        if not app: 
            app = QtWidgets.QApplication(sys.argv)
        myApp = AssetMoverUI()
        sys.exit(app.exec_())

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

class AssetMoverUI(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(AssetMoverUI, self).__init__(parent)
        # self.ui = ui.Ui_StillPublishUI()
        # self.ui.setupUi(self)
        uiFile = '%s/ui.ui' % moduleDir
        self.ui = load.loadUI(uiFile, self)
        self.ui.show()
        self.ui.setWindowTitle('Asset Mover v.0.0.1')

        self.columnName = ['Select', 'Asset Name', 'Type', 'SubType', 'res', 'Target', 'Source', 'Status', 'Progress']
        self.serverMode = True
        self.res = ['pr', 'lo', 'md', 'hi']
        self.dept = ['rig']
        self.resDefault = 'md'

        self.init_functions()
        self.init_signals()


    def init_functions(self): 
        self.set_table()
        self.set_project()
        self.set_res()
        self.set_dept()

    def init_signals(self): 
        self.ui.shotgun_radioButton.clicked.connect(partial(self.set_mode, False)) 
        self.ui.server_radioButton.clicked.connect(partial(self.set_mode, True)) 
        self.ui.listAsset_pushButton.clicked.connect(self.list_asset)
        self.ui.res_comboBox.currentIndexChanged.connect(self.set_item_res)
        self.ui.selectAll_checkBox.stateChanged.connect(self.select_all_items)
        self.ui.tableWidget.cellChanged.connect(self.cell_changed_trigger)
        self.ui.move_pushButton.clicked.connect(self.move_asset)

    def set_mode(self, mode): 
        self.serverMode = mode

    def set_table(self): 
        for row, each in enumerate(self.columnName): 
            ui_wrapper.insert_column(self.ui.tableWidget, each, columnIndex=row)

    def set_project(self): 
        if self.serverMode: 
            self.server = os.getenv(config.RFPROJECT)
            projects = sorted(file_utils.listFolder(self.server))

        self.ui.project_comboBox.addItems(projects)

    def set_res(self): 
        self.ui.res_comboBox.addItems(self.res)
        self.ui.res_comboBox.setCurrentIndex(self.res.index(self.resDefault))

    def set_dept(self): 
        self.ui.dept_comboBox.addItems(self.dept)


    def set_item_res(self): 
        index = self.ui.res_comboBox.currentIndex()
        comboBoxWidgets = ui_wrapper.get_tableWidget_all_items(self.ui.tableWidget, self.columnName.index('res'), widget=True)

        for comboBox in comboBoxWidgets: 
            comboBox.setCurrentIndex(index)


    def select_all_items(self, state): 
        if state: 
            state = QtCore.Qt.Checked
        else: 
            state = QtCore.Qt.Unchecked
        
        checkBoxs = ui_wrapper.get_tableWidget_all_items(self.ui.tableWidget, self.columnName.index('Select'), widget=True)

        for checkBox in checkBoxs: 
            checkBox.setCheckState(state)

    def get_check_items(self): 
        checkBoxs = ui_wrapper.get_tableWidget_all_items(self.ui.tableWidget, self.columnName.index('Select'), widget=True)
        rows = []

        for row, checkBox in enumerate(checkBoxs): 
            if checkBox.isChecked(): 
                rows.append(row)

        return rows 

    def get_asset_info(self, row): 
        project = str(self.ui.project_comboBox.currentText())
        step = str(self.ui.dept_comboBox.currentText())
        assetName = ui_wrapper.get_tableWidget_item(self.ui.tableWidget, row, self.columnName.index('Asset Name'), widget=False)
        assetType = ui_wrapper.get_tableWidget_item(self.ui.tableWidget, row, self.columnName.index('Type'), widget=False)
        subType = ui_wrapper.get_tableWidget_item(self.ui.tableWidget, row, self.columnName.index('SubType'), widget=False)
        source = ui_wrapper.get_tableWidget_item(self.ui.tableWidget, row, self.columnName.index('Source'), widget=False)
        status = ui_wrapper.get_tableWidget_item(self.ui.tableWidget, row, self.columnName.index('Status'), widget=False)
        resWidget = ui_wrapper.get_tableWidget_item(self.ui.tableWidget, row, self.columnName.index('res'), widget=True)
        res = str(resWidget.currentText())

        # {'project': 'project', 'entity'='asset', entitySub1='character', entitySub2='main', name='aiya', step=model, task='model_md'}
        asset = path_info.PathInfo(project=project, entity='asset', entitySub1=str(assetType.text()), entitySub2=str(subType.text()), name=str(assetName.text()), step=str(step))

        return {'asset': asset, 'source': str(source.text()), 'status': str(status.text()), 'res': res}


    def list_asset(self): 
        assetDict = self.get_assets()
        self.ui.tableWidget.blockSignals(True)

        ui_wrapper.clear_table(self.ui.tableWidget)
        project = str(self.ui.project_comboBox.currentText())
        step = str(self.ui.dept_comboBox.currentText())

        for row, value in assetDict.iteritems(): 
            baseColor = [255, 255, 255]
            assetColor = [255, 255, 255]

            if isMaya: 
                assetColor = [0, 0, 0]
                baseColor = [0, 0, 0]

            if value.get('duplicated'): 
                assetColor = [255, 200, 200]
                if isMaya: 
                    assetColor = [100, 0, 0]

            # asset 
            logger.debug(value.get('type'))
            logger.debug(value.get('subType'))
            logger.debug(value.get('asset'))
            asset = path_info.PathInfo(project=project, entity='asset', entitySub1=value.get('type'), entitySub2=value.get('subType'), name=value.get('asset'), step=step)

            ui_wrapper.insert_row(self.ui.tableWidget, row, height=20)
            ui_wrapper.fill_table(self.ui.tableWidget, row, self.columnName.index('Asset Name'), value.get('asset'), iconPath='', color=assetColor)
            ui_wrapper.fill_table(self.ui.tableWidget, row, self.columnName.index('Type'), value.get('type'), iconPath='', color=baseColor)
            ui_wrapper.fill_table(self.ui.tableWidget, row, self.columnName.index('SubType'), value.get('subType'), iconPath='', color=baseColor)
            ui_wrapper.fill_table(self.ui.tableWidget, row, self.columnName.index('Source'), '', iconPath='', color=baseColor)
            ui_wrapper.fill_table(self.ui.tableWidget, row, self.columnName.index('Status'), '', iconPath='', color=baseColor)

            # checkBox 
            checkBox = QtWidgets.QCheckBox()
            self.ui.tableWidget.setCellWidget(row, self.columnName.index('Select'), checkBox)

            # res comboBox 
            resComboBox = QtWidgets.QComboBox()
            resComboBox.addItems(self.res)
            resComboBox.setCurrentIndex(self.res.index(self.resDefault))
            self.ui.tableWidget.setCellWidget(row, self.columnName.index('res'), resComboBox)
            resComboBox.currentIndexChanged.connect(partial(self.set_dst_status, row, asset))

            # set file target status 
            self.set_dst_status(row, asset)

            # resize to fit contents 
            self.ui.tableWidget.resizeColumnToContents(self.columnName.index('Select'))
            self.ui.tableWidget.resizeColumnToContents(self.columnName.index('res'))
            self.ui.tableWidget.resizeColumnToContents(self.columnName.index('Target'))

        self.ui.tableWidget.blockSignals(False)


    def set_dst_status(self, row, asset, *args): 
        project = asset.project
        resWidget = ui_wrapper.get_tableWidget_item(self.ui.tableWidget, row, self.columnName.index('res'), widget=True)
        res = str(resWidget.currentText())
        libPath = '%s/%s' % (asset.libPath(), asset.libName(asset.step, res, project=False, ext='ma'))
        text = 'N/A' 
        assetColor = [255, 160, 160]

        if isMaya: 
            assetColor = [100, 0, 0]

        if os.path.exists(libPath): 
            stat = os.stat(libPath)
            text = '%s KB' % str(stat.st_size/1000)
            assetColor = [160, 255, 160]

            if isMaya: 
                assetColor = [0, 100, 0]

            if stat.st_size/1000 < 100: 
                assetColor = [255, 255, 160]

                if isMaya: 
                    assetColor = [100, 100, 0]

        ui_wrapper.fill_table(self.ui.tableWidget, row, self.columnName.index('Target'), text, iconPath='', color=assetColor)


    def get_assets(self): 
        row = 0
        assetDict = OrderedDict()
        assetList = []
        project = str(self.ui.project_comboBox.currentText())

        if self.serverMode: 
            assetPath = ('/').join([self.server, project, config.asset])
            types = sorted(file_utils.listFolder(assetPath))

            for assetType in types: 
                assetTypePath = ('/').join([assetPath, assetType])
                subTypes = sorted(file_utils.listFolder(assetTypePath))

                for subType in subTypes: 
                    assetEntityPath = ('/').join([assetTypePath, subType])
                    assets = sorted(file_utils.listFolder(assetEntityPath))

                    for asset in assets: 
                        dup = False 
                        if asset in assetList: 
                            dup = True
                            index = assetList.index(asset)
                            assetDict[index]['duplicated'] = True

                        assetDict.update({row: {'asset': asset, 'type': assetType, 'subType': subType, 'duplicated': dup}}) 
                        row+=1
                        assetList.append(asset)

        return assetDict

    def cell_changed_trigger(self, row, column): 
        if column == self.columnName.index('Source'): 
            sourceItem = self.ui.tableWidget.item(row, column)
            statusItem = QtWidgets.QTableWidgetItem()
            inputPath = str(sourceItem.text())

            
            if os.path.exists(inputPath) and os.path.splitext(inputPath)[-1] in ['.ma', '.mb']: 
                statusItem.setText('Ready')
                green = self.get_color(color='green')
                statusItem.setBackground(QtGui.QColor(green[0], green[1], green[2]))
                
                self.ui.tableWidget.blockSignals(True)
                sourceItem.setBackground(QtGui.QColor(green[0], green[1], green[2]))
                sourceItem.setText(inputPath.replace('\\', '/'))
                self.ui.tableWidget.blockSignals(False)

            else: 
                red = self.get_color(color='green')
                statusItem.setText('Path not exists')
                sourceItem.setBackground(QtGui.QColor(red[0], red[1], red[2]))
                statusItem.setBackground(QtGui.QColor(red[0], red[1], red[2]))

            self.ui.tableWidget.setItem(row, self.columnName.index('Status'), statusItem)


    def move_asset(self): 
        logger.info('move_asset')
        moveRows = self.get_check_items()
        
        for row in moveRows: 

            progressBar = QtWidgets.QProgressBar()
            self.ui.tableWidget.setCellWidget(row, self.columnName.index('Progress'), progressBar)
            progressBar.setMinimum(1)
            progressBar.setMaximum(100)

            assetDict = self.get_asset_info(row)
            asset = assetDict.get('asset')
            source = assetDict.get('source')
            status = assetDict.get('status')
            res = assetDict.get('res')
            libPath = '%s/%s' % (asset.libPath(), asset.libName(asset.step, res, project=False, ext='ma'))
            texturePath = asset.texturePath()

            if os.path.exists(source) and os.path.splitext(source)[-1] in ['.ma', '.mb']: 
                self.set_status(row, 'In progress...')
                # find assets linked 
                self.set_status(row, 'collecting assets ...')
                replaceDict = self.get_replace_info(asset, source, res, progressBar)
                self.set_status(row, 'collect asset complete')

                if replaceDict: 
                    # copy 
                    self.set_status(row, 'copying files ...')
                    self.copy_assets(replaceDict, progressBar)
                # copy scene 
                result = file_utils.copy(source, libPath)
                self.set_status(row, 'copy complete')

                if result: 
                    # repath 
                    self.set_status(row, 'repath ...')
                    
                    if not self.ui.maya_checkBox.isChecked(): 
                        pipeline_utils.search_replace_file(libPath, libPath, replaceDict)

                    else: 
                        self.replace_files(libPath, replaceDict)
                    
                    progressBar.setValue(100)
                    progressBar.hide()
                    logger.info('replace path success\n\n')
                    self.set_status(row, 'Finish')
                    print 'replace path success'
                    self.set_dst_status(row, asset)

            else: 
                self.set_status(row, 'File not valid. Stop.')

    def testProgressBar(self): 
        moveRows = self.get_check_items()
        import time

        for row in moveRows: 
            progressBar = QtWidgets.QProgressBar()
            progressBar.setMinimum(1)
            progressBar.setMaximum(100)
            self.ui.tableWidget.setCellWidget(row, self.columnName.index('Progress'), progressBar)

            for i in range(100): 
                time.sleep(0.01)
                progressBar.setValue(i)

            progressBar.hide()
            self.set_status(row, 'Finish')




    def get_replace_info(self, asset, source, res, progressBar): 
        processPercent = 30
        texturePath = '%s/%s' % (asset.texturePath(), res)

        if not self.ui.maya_checkBox.isChecked(): 
            assetInfoDict = maya_utils.getMayaSceneAssets(source.replace('/', '\\'), '2016', True)

        else: 
            assetInfoDict = self.get_maya_scene_assets(source)
        
        replaceDict = dict()

        # copy file/texture 
        if assetInfoDict: 
            # refs = assetInfoDict.get('files')
            textures = assetInfoDict.get('textureFiles')
            # asmFiles = assetInfoDict.get('assemblyFiles')
            allFiles = [a[0] for a in textures]
            replaceDict = dict()

            for search in allFiles: 
                basename = os.path.basename(search)
                replace = '%s/%s' % (texturePath, basename)
                replaceDict.update({search: replace})

            progressBar.setValue(processPercent)

        return replaceDict


    def get_maya_scene_assets(self, source): 
        mc.file(source, force=True , open=True, loadReferenceDepth = "all")
        logger.info('open %s' % source)

        files = mc.file(query=1, list=1, withoutCopyNumber=1)
        logger.info('find all refs %s' % files)

        assemblyFiles = maya_utils.getAssemblyFiles()
        # assemblyFiles = getAssemblyFiles()
        textureFiles = maya_utils.getTextureFile()
        tmpFile = 'mayaAssetList.txt'
        tmpdir = os.getenv('TMPDIR')
        tmpPath = '%s/%s' % (tmpdir, tmpFile)

        data = {'files': files, 'assemblyFiles': assemblyFiles, 'textureFiles': textureFiles}

        return data


    def copy_assets(self, replaceDict, progressBar): 
        logger.info('start copying ...')
        processPercent = 50
        num = 0 
        value = progressBar.value()
        increment = processPercent/len(replaceDict.keys())

        for src, dst in replaceDict.iteritems(): 
            result = file_utils.copy(src, dst)
            logger.debug('copied %s' % result)

            if result: 
                num+=1
                progressBar.setValue(num*increment)
                QtWidgets.QApplication.processEvents()

        logger.info('copy %s files success' % num)


    def replace_files(self, mayaPath, replaceDict): 
        fileNodes = mc.ls(type='file')

        for node in fileNodes: 
            path = mc.getAttr('%s.fileTextureName' % node)

            if path in replaceDict.keys(): 
                newPath = replaceDict.get(path)
                mc.setAttr('%s.fileTextureName' % node, newPath, type='string')

        mc.file(rename=mayaPath)
        print mayaPath
        result = mc.file(save=True, f=True)


    def set_status(self, row, message): 
        status = ui_wrapper.get_tableWidget_item(self.ui.tableWidget, row, self.columnName.index('Status'), widget=False)
        status.setText(message)
        logger.info(message)
        QtWidgets.QApplication.processEvents()

    def get_color(self, color): 
        red = [255, 160, 160]
        green = [160, 255, 160]
        blue = [160, 160, 255]

        if isMaya: 
            red = [100, 0, 0]
            green = [0, 100, 0]
            blue = [0, 0, 100]

        if color == 'red': 
            return red 
        if color == 'green': 
            return green 
        if color == 'blue': 
            return blue 



""" for standalone run this """
if __name__ == '__main__':
    show()

