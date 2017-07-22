# v.0.0.1 basic ui working

#Import python modules
import sys, os, re, subprocess, inspect
import platform
import getpass
import traceback
import logging
moduleDir = os.path.dirname(sys.modules[__name__].__file__)
from inspect import getmembers, isfunction

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
    reload(setEnv)
    setEnv.set()

from rftool.utils import log_utils
reload(log_utils)
from rftool.utils.ui import load

logFile = log_utils.name('still_publish_tool', user=getpass.getuser())
logger = log_utils.init_logger(logFile)
logger.setLevel(logging.INFO)

os.environ['QT_PREFERRED_BINDING'] = os.pathsep.join(['PySide', 'PySide2'])
from Qt import wrapInstance
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui


#Import GUI
# from PySide import QtCore
# from PySide import QtGui
# import ui

from functools import partial

#import rftool commands
# from rftool import publish
from rftool.utils import file_utils
from rftool.utils import path_info
from rftool.utils import sg_wrapper
from rftool.utils import sg_process
from rftool.publish.utils import pub_utils
from rftool.utils.ui import combo_browser_widget
from rftool.utils.ui import pipeline_widget
from startup import config
import publish_core

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
        uiName = 'StillPublishUI'
        deleteUI(uiName)
        myApp = RFStillPublish(getMayaWindow())
        # myApp.show()
        return myApp

    else:
        logger.info('Run in standalone\n')
        app = QtWidgets.QApplication.instance()
        if not app: 
            app = QtWidgets.QApplication(sys.argv)
        myApp = RFStillPublish()
        # myApp.show()
        sys.exit(app.exec_())

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

class RFStillPublish(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(RFStillPublish, self).__init__(parent)
        # self.ui = ui.Ui_StillPublishUI()
        # self.ui.setupUi(self)
        uiFile = '%s/ui.ui' % moduleDir

        if isMaya: 
            self.ui = load.loadUIMaya(uiFile, self)
        else: 
            self.ui = load.loadUI(uiFile, self)
        self.ui.show()
        self.setWindowTitle('RF Still Publish v.0.0.1')

        self.pathInfo = path_info.PathInfo()

        self.imageFormat = ['.jpg', '.png', '.jpeg']
        self.snapFormat = 'png'

        publish_core.ui = self

        self.set_ui()
        self.init_signals()
        self.init_functions()

    def set_ui(self):
        """ instance custom widget """
        logger.debug('setting ui ...')

        # set mode
        self.set_mode('manual')

        self.ui.projectPlc_frame.setVisible(False)

        # instance sg status widget
        self.statusWidget = pipeline_widget.StatusWidget()
        self.statusWidget.set_task_status(limit=pipeline_widget.status_config.publishStatuses)

        # instance project browser
        self.projectWidget = combo_browser_widget.ProjectBrowser(root=os.environ[config.RFPROJECT], mode=self.entity_mode, pathInfo=self.pathInfo)
        self.ui.project_layout.addWidget(self.projectWidget)

        # instance sg task widget
        self.taskWidget = pipeline_widget.TaskWidget()
        self.userWidget = pipeline_widget.UserWidget()

        # instance step widget
        self.stepWidget = pipeline_widget.StepWidget(pathInfo=self.pathInfo)
        self.stepWidget.list_steps()

        # instance snap widget
        self.ui.publish_listWidget.setVisible(False)
        
        if isMaya: 
            self.snapWidget = pipeline_widget.SnapImageMayaWidget(formats=self.imageFormat, snapFormat=self.snapFormat, parent=self)

        # instance publish widget 
        self.publishWidget = pipeline_widget.PublishListWidget()
        self.publishWidget.label.setText('Publish : ')
            
        # self.snapWidget = pipeline_widget.SnapImageWidget(formats=self.imageFormat, isMaya=isMaya, parent=self)

        # instance source widget
        self.ui.source_lineEdit.setVisible(False)
        self.sourceFileWidget = pipeline_widget.DropPathWidget(self)

        # logo 
        self.logoLabel = QtWidgets.QLabel()

        # publish label 
        self.publishVersionLabel = QtWidgets.QLabel()
        self.publishVersionLabel.setText('-')

        # instance description widget 
        self.descriptionWidget = QtWidgets.QPlainTextEdit()
        self.descriptionWidget.setMaximumSize(QtCore.QSize(16777215, 100))

        # force publish checkBox
        self.forcePublishCheckBox = QtWidgets.QCheckBox()
        self.forcePublishCheckBox.setText('Force error publish')

        # file publish 
        self.filePublishCheckBox = QtWidgets.QCheckBox()
        self.filePublishCheckBox.setText('File Publish')

        # debug checkBox
        self.debugCheckBox = QtWidgets.QCheckBox()
        self.debugCheckBox.setText('Debug')


        # parent in ui
        self.ui.gridLayout.addWidget(self.taskWidget, 0, 1)
        self.ui.gridLayout.addWidget(self.statusWidget, 1, 1)
        self.ui.gridLayout.addWidget(self.userWidget, 2, 1)
        self.ui.gridLayout.setVerticalSpacing(0)
        self.ui.gridLayout.setColumnStretch(0, 1)
        self.ui.gridLayout.setColumnStretch(1, 2)

        self.ui.department_horizontalLayout.addWidget(self.stepWidget)
        self.ui.department_horizontalLayout.setStretch(0, 1)
        self.ui.department_horizontalLayout.setStretch(1, 2)

        self.ui.header_horizontalLayout.addWidget(self.publishVersionLabel)
        self.ui.header_horizontalLayout.addWidget(self.logoLabel)

        self.ui.header_horizontalLayout.setStretch(0, 0)
        self.ui.header_horizontalLayout.setStretch(1, 1)
        self.ui.header_horizontalLayout.setStretch(2, 0)

        self.ui.snap_verticalLayout.addWidget(self.filePublishCheckBox, 0, 0)
        self.ui.snap_verticalLayout.addWidget(self.snapWidget)
        self.ui.snap_verticalLayout.setStretch(1, 0)
        self.ui.snap_verticalLayout.setStretch(2, 0)
        self.ui.snap_verticalLayout.setStretch(3, 3)
        # self.ui.snap_verticalLayout.setStretch(2, 1)

        self.ui.horizontalLayout_3.addWidget(self.sourceFileWidget)

        self.ui.publish_verticalLayout.addWidget(self.publishWidget)
        self.ui.publish_verticalLayout.addWidget(self.descriptionWidget)
        self.ui.publish_verticalLayout.addWidget(self.forcePublishCheckBox)
        self.ui.publish_verticalLayout.addWidget(self.debugCheckBox)
        self.ui.publish_verticalLayout.setStretch(0, 0)
        self.ui.publish_verticalLayout.setStretch(1, 2)
        self.ui.publish_verticalLayout.setStretch(2, 0)
        self.ui.publish_verticalLayout.setStretch(3, 0)
        self.ui.publish_verticalLayout.setStretch(4, 0)

        # set progress bar
        self.ui.progressBar.setVisible(False)
        logger.debug('setting ui done')

        # publish button disable
        # self.ui.publish_pushButton.setEnabled(False)
        self.ui.design_radioButton.setVisible(False)

        if isMaya:
            # set source input
            if self.pathInfo.path:
                self.sourceFileWidget.widget.setText(self.pathInfo.path)
                self.sourceFileWidget.widget.setEnabled(False)
                self.set_mode('automatic')
                self.projectWidget.enable(False)
                self.stepWidget.enable(False)

        # set publish version 
        self.set_publish_version()




    def init_signals(self):
        """ connecting signals """
        logger.debug('init signals ...')

        # project widget connected signal
        self.projectWidget.entityChanged.connect(self.set_task)

        # department widget connected signal also
        self.stepWidget.widget.currentIndexChanged.connect(self.set_task)

        # entity mode signal
        self.ui.asset_radioButton.clicked.connect(partial(self.mode_change, 'Asset'))
        self.ui.scene_radioButton.clicked.connect(partial(self.mode_change, 'Shot'))

        # status signal 
        self.statusWidget.widget.currentIndexChanged.connect(self.status_signal)

        # snapWidget
        self.snapWidget.itemClicked.connect(lambda x: self.set_preview(x, 600, 400))

        # preview picture
        logger.debug('init signals done')

        # publish signal
        self.ui.publish_pushButton.clicked.connect(self.publish)

        # publish detail signal 
        self.publishWidget.currentItemChanged.connect(self.set_func_description)

        # file Publish signal. checkBox to export file or just review
        self.filePublishCheckBox.stateChanged.connect(self.load_publish_list)

        # source version / task change 
        self.sourceFileWidget.widget.returnPressed.connect(self.set_publish_version)
        self.taskWidget.widget.currentIndexChanged.connect(self.set_publish_version)

        # debug 
        self.debugCheckBox.stateChanged.connect(self.set_debug)


    def init_functions(self):
        logger.info('start browsing ...')
        self.projectWidget.browsing()
        logger.info('finish browsing')

        logger.info('load publish list ...')
        self.load_publish_list()
        logger.info('load complete')


    def set_task(self, arg=None):
        logger.debug('setting task ...')

        self.taskWidget.widget.clear()
        project = str(self.projectWidget.projectComboBox.currentText())
        logger.debug('project : %s' % project)

        filter1 = str(self.projectWidget.entitySub1ComboBox.currentText())
        logger.debug('filter1 : %s' % filter1)

        filter2 = str(self.projectWidget.entitySub2ComboBox.currentText())
        logger.debug('filter2 : %s' % filter2)

        entity = str(self.projectWidget.entityComboBox.currentText())
        logger.debug('entity : %s' % entity)

        step = self.stepWidget.step()
        logger.debug('step : %s' % step)


        if project and entity:
            self.taskWidget.set_task(self.entity_mode, project, entity, step=step, setBlank=True)
            logger.info('set task done')


    def set_preview(self, filename, w, h):
        logger.info('Preview %s at %s x %s' % (filename, w, h))
        self.ui.preview_label.setPixmap(QtGui.QPixmap(filename).scaled(w, h, QtCore.Qt.KeepAspectRatio))


    # publish parts 
    def load_publish_list(self): 
        filePublish = self.filePublishCheckBox.isChecked()
        preset = 'wip'
        if filePublish: 
            preset = 'filePublish'

        publDict = publish_core.load_publish_list(self.pathInfo, preset)
        self.publishWidget.listWidget.clear()

        if publDict: 
            pubFunc, publList = publDict['publ']
            deptFunc, deptPublList = publDict['deptPubl']
            precheckFunc, precheckList = publDict['precheckList']
            sg_publish, sgPublList = publDict['sgPubls']
            post_publish, postPublList = publDict['postPubl']

            # pass ui object to other funcs
            pubFunc.ui = self
            precheckFunc.ui = self
            deptFunc.ui = self
            sg_publish.ui = self
            post_publish.ui = self

            status = True

            for check in precheckList: 
                display, func = check
                message = func.__doc__
                data = {'func': func, 'status': status, 'message': message}
                item = self.publishWidget.add_item(display, data=data, description='precheck', checkStateEnable=False)
                self.publishWidget.set_item_status(item, 'ready')

            for publ in publList: 
                display, func = publ
                message = func.__doc__
                data = {'func': func, 'status': status, 'message': message}
                item = self.publishWidget.add_item(display, data=data, description='publish', checkStateEnable=False)
                self.publishWidget.set_item_status(item, 'ready')

            for publ in deptPublList: 
                display, func = publ
                message = func.__doc__
                data = {'func': func, 'status': status, 'message': message}
                item = self.publishWidget.add_item(display, data=data, description=self.pathInfo.step, checkStateEnable=True)
                self.publishWidget.set_item_status(item, 'ready')

            for publ in sgPublList: 
                display, func = publ
                message = func.__doc__
                data = {'func': func, 'status': status, 'message': message}
                item = self.publishWidget.add_item(display, data=data, description='shotgun', checkStateEnable=True)
                self.publishWidget.set_item_status(item, 'ready')

            for publ in postPublList: 
                display, func = publ
                message = func.__doc__
                data = {'func': func, 'status': status, 'message': message}
                item = self.publishWidget.add_item(display, data=data, description='postPublish', checkStateEnable=True)
                self.publishWidget.set_item_status(item, 'ready')
            # self.publishWidget.listWidget.add_item(deptPublList)


    # signal areas 
    def set_publish_version(self): 
        """ set publish version based on source input """ 
        task = self.taskWidget.get_task()

        if task: 
            logger.debug('set publish version')
            
            source = str(self.sourceFileWidget.widget.text())
            entity = path_info.PathInfo(source)
            entity.task = task.get('content')

            publishFile, saveWorkFile, incrementSaveWorkFile, libFile = pub_utils.get_publish_info(entity)
            self.publishVersionLabel.setText(publishFile)

            # set entity from source **
            self.pathInfo = path_info.PathInfo(source)
            
            logger.debug('version %s' % os.path.basename(publishFile))


    def status_signal(self): 
        """ signal from changing status """ 
        status = self.statusWidget.get_task_status()
        filePublish = True
        if status in publish_core.filePublishPreset.keys(): 
            filePublish = publish_core.filePublishPreset[status]

        if filePublish: 
            self.filePublishCheckBox.setEnabled(False)
            self.filePublishCheckBox.setChecked(True)
        else: 
            self.filePublishCheckBox.setEnabled(True)
            self.filePublishCheckBox.setChecked(False)


    def set_debug(self, state): 
        """ set log to debug """ 
        if state: 
            level = logging.DEBUG
        else: 
            level = logging.INFO

        logger.setLevel(level)
        logger.info('set logging level to %s' % level)


    def publish(self): 
        # read list 
        logger.info('Start publishing ...')
        infoComplete, details, uiInfo = self.check_ui_completion()

        if infoComplete: 
            taskEntity = uiInfo.get('task')
            taskName = taskEntity.get('content')
            errorList = False
            
            # set publish entity object from source lineEdit ** very important here 
            entity = path_info.PathInfo(uiInfo.get('source'))
            entity.task = taskName

            publLists = [self.publishWidget.listWidget.item(row) for row in range(self.publishWidget.listWidget.count())]

            for item in publLists: 
                # get process type
                widget = self.publishWidget.listWidget.itemWidget(item)
                processName = widget.text()
                processType = widget.description()
                state = widget.get_checked_state()

                if state: 
                    # get data 
                    data = item.data(QtCore.Qt.UserRole)
                    func = data.get('func')
                    message = data.get('message')

                    # set icon ui inprogress 
                    self.publishWidget.set_item_status(item, 'ip')

                    # run function
                    try: 
                        logger.info(processName)
                        
                        if processType == 'precheck': 
                            result, message = func()
                        
                        else: 
                            # other functions has entity as argument
                            returnValue = func(entity)

                            result = False
                            message = 'No return value from "%s"' % func.__name__
                            if returnValue: 
                                result, message = returnValue

                        data.update({'message': message})
                    
                    except Exception as e: 
                        # store traceback to var 
                        error = traceback.format_exc()
                        traceback.print_exc()
                        data.update({'message': error})

                        logger.error(error)
                        result = False
                    
                    # set item status ui
                    self.publishWidget.set_item_status(item, result)
                    
                    # update publish value  
                    data.update({'status': result})
                    item.setData(QtCore.Qt.UserRole, data)

                    if processType == 'precheck': 
                        if result == False: 
                            QtWidgets.QMessageBox.warning(self, 'Warning', '%s failed.' % processName)
                            logger.warning('precheck failed.')
                            errorList = True
                            break

                    if not self.forcePublishCheckBox.isChecked() and result == False: 
                        QtWidgets.QMessageBox.warning(self, 'Error', '%s failed.' % processName)
                        logger.error('%s failed' % processName)
                        errorList = True
                        
                        # disable publish push button
                        self.ui.publish_pushButton.setEnabled(False)
                        break

                    QtWidgets.QApplication.processEvents()

            # complete 

            # dialog 
            
            if not errorList: 
                dialogMessage = 'Publish complete'
                QtWidgets.QMessageBox.information(self, 'Complete', dialogMessage)

                # disable publish push button
                self.ui.publish_pushButton.setEnabled(False)

        else: 
            logger.debug('Please complete ui selection')
            QtWidgets.QMessageBox.warning(self, 'Incomplete Data', 'Please complete the following details\n%s' % '\n'.join(details))


    def set_func_description(self, item): 
        data = item.data(QtCore.Qt.UserRole)
        message = data.get('message')
        status = data.get('status')
        self.descriptionWidget.setPlainText(message)

        if status: 
            self.descriptionWidget.setStyleSheet('')
        
        else: 
            self.descriptionWidget.setStyleSheet("color: rgb(200, 0, 0);")


    def check_ui_completion(self): 
        info = dict()
        incomplete = []
        
        # check task 
        task = self.taskWidget.get_task()
        info.update({'task': task})
        
        if not task: 
            incomplete.append('- task not selected')

        # check source 
        source = str(self.sourceFileWidget.widget.text())
        info.update({'source': source})
        
        if not source: 
            incomplete.append('- file has no name')

        # check screen shot 
        items = self.snapWidget.get_all_items()
        info.update({'snap': items})

        if not items: 
            incomplete.append('- no screen shot')

        # summary 
        if not all(info[a] for a in info.keys()): 
            return False, incomplete, info 

        return True, incomplete, info

    @property
    def entity_mode(self):
        if self.ui.design_radioButton.isChecked():
            return 'design'
        if self.ui.asset_radioButton.isChecked():
            return 'asset'
        if self.ui.scene_radioButton.isChecked():
            return 'scene'

    def mode_change(self, mode):
        """ signal when mode switch changed """
        logger.debug('mode changed to -%s' % mode)

        # block step signal, so it won't call when clear and item added
        self.stepWidget.widget.blockSignals(True)
        self.stepWidget.list_steps(entityType=mode)
        self.stepWidget.widget.blockSignals(False)

        # recall list_task again
        self.set_task()

    def set_mode(self, mode):
        self.ui.mode_label.setAlignment(QtCore.Qt.AlignCenter)
        if mode == 'manual':
            bgColor = [200, 140, 0]
            textColor = [0, 0, 0]
            text = 'Manual Mode'


        if mode == 'automatic':
            bgColor = [20, 160, 0]
            textColor = [200, 200, 200]
            text = 'Automatic Mode'

        self.ui.mode_label.setText(text)
        bgStr = 'background-color: rgb(%s, %s, %s);' % (bgColor[0], bgColor[1], bgColor[2])
        textStr = 'color: rgb(%s, %s, %s);' % (textColor[0], textColor[1], textColor[2])
        styleStr = ('\n').join([bgStr, textStr])
        self.ui.mode_label.setStyleSheet('''
                                QLabel {
                                %s
                                }''' % styleStr)



""" for standalone run this """
if __name__ == '__main__':
    show()
