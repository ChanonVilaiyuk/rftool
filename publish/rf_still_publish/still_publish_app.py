# v.0.0.1 basic ui working

#Import python modules
import sys, os, re, subprocess, inspect
import platform
import getpass

#Import maya commands
try:
    import maya.cmds as mc
    import maya.mel as mm
    import maya.OpenMayaUI as mui
    from shiboken import wrapInstance
    isMaya = True
except ImportError:
    isMaya = False
    packagePath = '%s/python/2.7/site-packages' % os.environ['RFSCRIPT']
    toolPath = '%s/core/maya' % os.environ['RFSCRIPT']
    corePath = '%s/core' % os.environ['RFSCRIPT']
    appendPaths = [packagePath, toolPath, corePath]

    # add PySide lib path
    for path in appendPaths:
        if not path in sys.path:
            sys.path.append(path)

    from startup import setEnv
    reload(setEnv)
    setEnv.set()

from rftool.utils import log_utils
reload(log_utils)

logFile = log_utils.name('still_publish_tool', user=getpass.getuser())
logger = log_utils.init_logger(logFile)


#Import GUI
from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools
import ui

from functools import partial

#import rftool commands
# from rftool import publish
from rftool.utils import file_utils
from rftool.utils import path_info
from rftool.utils import sg_wrapper
from rftool.utils import sg_process
from rftool.utils.ui import combo_browser_widget
from rftool.utils.ui import pipeline_widget
from startup import config

module_path = sys.modules[__name__].__file__
module_dir  = os.path.dirname(module_path)


# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtGui.QWidget)

logger.info('\n\n==============================================')

def show():
    if isMaya:
        logger.info('Run in Maya\n')
        uiName = 'StillPublishUI'
        deleteUI(uiName)
        myApp = RFStillPublish(getMayaWindow())
        myApp.show()
        return myApp

    else:
        logger.info('Run in standalone\n')
        app = QtGui.QApplication(sys.argv)
        myApp = RFStillPublish()
        myApp.show()
        sys.exit(app.exec_())

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

class RFStillPublish(QtGui.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(RFStillPublish, self).__init__(parent)
        self.ui = ui.Ui_StillPublishUI()
        self.ui.setupUi(self)
        self.setWindowTitle('RF Still Publish v.0.0.1')

        self.pathInfo = path_info.PathInfo()

        self.imageFormat = ['.jpg', '.png', '.jpeg']

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
        self.projectWidget = combo_browser_widget.ProjectBrowser(root=config.rootWork, mode=self.entity_mode, pathInfo=self.pathInfo)
        self.ui.project_layout.addWidget(self.projectWidget)

        # instance sg task widget
        self.taskWidget = pipeline_widget.TaskWidget()
        self.userWidget = pipeline_widget.UserWidget()

        # instance step widget
        self.stepWidget = pipeline_widget.StepWidget(pathInfo=self.pathInfo)
        self.stepWidget.list_steps()

        # instance snap widget
        self.ui.publish_listWidget.setVisible(False)
        self.snapWidget = pipeline_widget.SnapImageWidget(formats=self.imageFormat, parent=self)

        # instance source widget
        self.ui.source_lineEdit.setVisible(False)
        self.sourceFileWidget = pipeline_widget.SetUrlWidget(self)


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
        self.ui.snap_verticalLayout.addWidget(self.snapWidget)
        self.ui.horizontalLayout_3.addWidget(self.sourceFileWidget)

        # set progress bar
        self.ui.progressBar.setVisible(False)
        logger.debug('setting ui done')

        # publish button disable
        self.ui.publish_pushButton.setEnabled(False)
        self.ui.design_radioButton.setVisible(False)

        if isMaya:
            # set source input
            if self.pathInfo.path:
                self.sourceFileWidget.widget.setText(self.pathInfo.path)
                self.set_mode('automatic')
                self.projectWidget.enable(False)
                self.stepWidget.enable(False)

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

        # snapWidget
        self.snapWidget.itemClicked.connect(lambda x: self.set_preview(x, 600, 400))

        # preview picture
        logger.debug('init signals done')

    def init_functions(self):
        logger.info('start browsing ...')
        self.projectWidget.browsing()
        logger.info('finish browsing')

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
            self.taskWidget.set_task_status(self.entity_mode, project, entity, step=step, setBlank=True)
            logger.info('set task done')

    def set_preview(self, filename, w, h):
        logger.info('Preview %s at %s x %s' % (filename, w, h))
        self.ui.preview_label.setPixmap(QtGui.QPixmap(filename).scaled(w, h, QtCore.Qt.KeepAspectRatio))


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
        self.ui.mode_label.setAlignment(QtCore.Qt.AlignCenter);
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
