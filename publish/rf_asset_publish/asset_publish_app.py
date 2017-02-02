#Import python modules
import sys, os, re, shutil, random, subprocess, inspect

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

#import rftool commands
# from rftool import publish 
from rftool.utils import file_utils
from rftool.utils import path_info
from rftool.utils import maya_utils
from rftool.utils import sg_wrapper
from rftool.utils import sg_process
from rftool.publish.utils import pub_utils
from startup import config

module_path = sys.modules[__name__].__file__
module_dir  = os.path.dirname(module_path)

import maya.OpenMayaUI as mui

# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtGui.QWidget)

def show():
    uiName = 'asset_publish_UI'
    deleteUI(uiName)
    myApp = AssetPublish(getMayaWindow())
    # myApp.show()

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

class AssetPublish(QtGui.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(AssetPublish, self).__init__(parent)

        self.runUI()
        self.initial_UI()
        self.init_connect()

    def runUI(self):
    	loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(module_dir + "/ui.ui")
        file.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()

        self.ui.show()

    def initial_UI(self):

        try:
            self.asset = path_info.PathInfo()
            self.this_path = self.asset.path
            self.project = self.asset.project
            self.version_name = self.asset.versionNoUser
            self.version = file_utils.find_version(self.this_path)
            self.type_name = self.asset.type
            self.subtype_name = self.asset.subtype
            self.asset_name = self.asset.name
            self.department = self.asset.step
            # self.user_name = self.scene.user
            self.src_pub_path = self.asset.entityPath(root='RFPUBL') + '/srcPublish/' + self.version_name
            # self.pub_path = self.asset.entityPath(root='RFPUBL') + '/srcPublish/' + self.version_name
            self.prod_dir = self.asset.entityPath(root='RFPROD')
            self.image_prod = self.asset.entityPath(root='RFPROD') + '/images/' + self.version_name
            self.image_publ = self.asset.entityPath(root='RFPUBL') + '/images/' + self.version_name
            self.image_path_no_ext = self.image_prod + '/' + self.version_name

            self.movie_prod = self.asset.entityPath(root='RFPROD') + '/movies/' + self.version_name
            self.movie_publ = self.asset.entityPath(root='RFPUBL') + '/movies/' + self.version_name
            
            self.thumbnail = ''
            self.movie = ''

            self.set_ui_information()
            self.get_thumbnail_version()
            self.get_sg_data()

        except AttributeError as attrErr :
            print attrErr, ',', self.this_path
            QtGui.QMessageBox.warning(self, 'Warning', 'No Maya Scene Open')

    def init_connect(self):
        self.ui.action_add_check_up.triggered.connect(self.add_checkup_lists)
        self.ui.screen_capture_pushButton.clicked.connect(self.screen_capture)
        self.ui.upload_movie_pushButton.clicked.connect(self.upload_movie)
        self.ui.autoCheck_pushButton.clicked.connect(self.auto_check)
        self.ui.review_pushButton.clicked.connect(self.review)

        self.ui.low_checkBox.toggled.connect(self.check_res)
        self.ui.med_checkBox.toggled.connect(self.check_res)
        self.ui.high_checkBox.toggled.connect(self.check_res)

        self.ui.publish_pushButton.clicked.connect(self.publish)

    def set_ui_information(self):
        self.email_name = { 'model': 'model@riffanimation.com', 'rig': 'rig@riffanimation.com', 'texture': 'texture@riffanimation.com', 'shade': 'shade@riffanimation.com' }

        self.main_styleSheet = 'QPushButton {\n    background-color: rgb(100, 200, 0);\n    border-style: inset;\n    border-width: 1px;\n    border-radius: 6px;\n    border-color: rgb(10, 90, 0);\n    font: bold 12px;\n}\nQPushButton:pressed {\n    background-color: rgb(15, 125, 15);\n}'
        self.sub_styleSheet = 'QPushButton {\n    background-color: rgb(255, 100, 0);\n    border-style: inset;\n    border-width: 1px;\n    border-radius: 6px;\n    border-color: rgb(100, 25, 0);\n    font: bold 11px;\n}\nQPushButton:pressed {\n    background-color: rgb(20, 20, 20);\n}'
        self.none_styleSheet = 'QPushButton {\n    background-color: rgb(115, 115, 115);\n    border-style: inset;\n    border-width: 1px;\n    border-radius: 6px;\n    border-color: rgb(100,25, 0);\n    font: bold 11px;\n}\nQPushButton:pressed {\n    background-color: rgb(160, 160, 160);\n}'

        self.ui.publish_pushButton.setStyleSheet(self.none_styleSheet)
        self.ui.publish_pushButton.setEnabled(False)
        self.ui.version_lineEdit.setText(self.version_name)
        self.ui.type_lineEdit.setText(self.type_name)
        self.ui.subtype_lineEdit.setText(self.subtype_name)
        self.ui.name_lineEdit.setText(self.asset_name)
        self.ui.department_lineEdit.setText(self.department)

    def get_thumbnail_version(self):
        if os.path.exists(self.image_prod):
            media_list = file_utils.listFile(self.image_prod)
            if media_list :

                for media in media_list:
                    if media.split('.')[-1] in ['mov','avi','mp4']:
                        self.movie = self.asset.entityPath(root='RFPROD') + '/movies/' + media_list
                        break

                        self.set_movie()

                if '.jpg' in media_list[-1]:
                    self.thumbnail = self.image_prod + '/' + media_list[-1]
                    self.set_thumbnail()
                
    def get_sg_data(self):
        self.sg_asset = sg_process.get_one_asset(self.project,self.asset_name)
        self.sg_tasks = sg_process.get_tasks_by_step(self.sg_asset,self.department)

        for task in self.sg_tasks:
            if 'lo' in task['content'].lower():
                self.ui.low_checkBox.setChecked(True)
            if 'md' in task['content'].lower():
                self.ui.med_checkBox.setChecked(True)
            if 'hi' in task['content'].lower():
                self.ui.high_checkBox.setChecked(True)

            if task['sg_status_list'] == 'apr':
                self.trace('Ready for Publish')
                self.ui.publish_pushButton.setStyleSheet(self.main_styleSheet)
                self.ui.publish_pushButton.setEnabled(True)


    def add_checkup_lists(self):
        module_publish = os.path.dirname(module_dir) + '/utils/check_' + self.department + '.py'
        module_publish = module_publish.replace('/','\\')
        subprocess.Popen('explorer /select,"%s"' %(module_publish))

    def screen_capture(self):
        image_path = file_utils.find_next_image_path('%s.jpg' %(self.image_path_no_ext))
        maya_utils.setup_asset_viewport_capture()
        self.thumbnail = maya_utils.playblast_capture_1k(image_path)
        # print self.thumbnail

        if self.thumbnail:
            self.set_thumbnail()

    def set_thumbnail(self):
        self.ui.thumbnail_label.clear()
        pixmap = QtGui.QPixmap(self.thumbnail)
        pixmap = pixmap.scaled(430, 430, QtCore.Qt.KeepAspectRatio)
        self.ui.thumbnail_label.setPixmap(pixmap)

    def set_movie(self):
        self.ui.movie_lineEdit.setText(self.movie)

    def upload_movie(self):
        workspace = mc.workspace(q=True,dir=True)
        fileName = QtGui.QFileDialog.getOpenFileName(self,"Open Movie", workspace + '/movies', "Movie Files (*.mov *.avi *.mp4)")
        self.movie = self.movie_prod + '.' + fileName[0].split('.')[-1]

        self.trace('Copying Movie to Server')
        file_utils.copy(fileName[0], self.movie)
        
        self.set_movie()

    # def create_turntable(self):
    #     self.turntable = ''
    #     pass

    def check_res(self):
        if not self.ui.low_checkBox.isChecked() and not self.ui.med_checkBox.isChecked() and not self.ui.high_checkBox.isChecked() :
            QtGui.QMessageBox.warning(self, 'Warning', 'You can\'t unchecked all resolution checkboxs. Check \'MED\' resolution.')
            self.ui.med_checkBox.setChecked(True)


    def check_task_resolution(self):
        res = []

        if self.ui.med_checkBox.isChecked():
            res.append('md')
        if self.ui.low_checkBox.isChecked():
            res.append('lo')
        if self.ui.high_checkBox.isChecked():
            res.append('hi')

        return res

    def get_email(self):
        
        self.send_email = ''

        if self.ui.model_checkBox.isChecked():
            self.send_email = self.email_name['model']
        if self.ui.rig_checkBox.isChecked():
            self.send_email = self.email_name['rig']
        if self.ui.texture_checkBox.isChecked():
            self.send_email = self.email_name['texture']
        if self.ui.shade_checkBox.isChecked():
            self.send_email = self.email_name['shade']
        

    def get_message(self):
        self.message = str(self.ui.message_plainTextEdit.toPlainText())
        # print self.message

    def auto_check(self):
        # check_module = 'check_' + self.department
        # # all_functions = inspect.getmembers(check_module, inspect.isfunction)

        chk_dup = maya_utils.check_duplicate_name()

        if not chk_dup:
            QtGui.QMessageBox.warning(self, 'Warning', 'Duplicated names exist.\nPlease check in outliner and rename them before publish.')
            self.ui.publish_pushButton.setStyleSheet(self.none_styleSheet)
            self.ui.publish_pushButton.setEnabled(False)

        else:
            self.trace('No duplicate name exists.')
            self.ui.publish_pushButton.setStyleSheet(self.main_styleSheet)
            self.ui.publish_pushButton.setEnabled(True)

    def trace(self,status):
        self.ui.status_label.setText(status)
        QtGui.QApplication.processEvents()

    def review(self):
        version_status = 'rev'
        task_status = 'rev'
        resolution = self.check_task_resolution()
        
        self.get_message()

        if self.thumbnail:
            
            for res in resolution:
                version_res = '_'.join([self.asset_name,self.department,res,self.version])
                task_res = '_'.join([self.department,res])
                
                task_ent = [ n for n in self.sg_tasks if task_res == n['content'] ]

                self.trace('Create \"%s\" Version on Shotgun' %(version_res))
                pub_utils.create_sg_version(self.project, self.sg_asset, version_res, task_ent[0], version_status ,self.thumbnail, self.message, self.movie)
            
            increment = pub_utils.create_increment_work_file(self.this_path)
            self.trace('Increment File to %s' %(increment.split('/')[-1]))

            self.trace('Update \"Pending for Review\" Status on Shotgun')
            pub_utils.set_sg_status(self.sg_tasks,'rev')
            
            self.trace('Submit Completed!!')
            QtGui.QMessageBox.information(self, 'Information', 'Submit Completed!!')

        if not self.thumbnail:
            self.trace('No thumbnail Image')
            QtGui.QMessageBox.warning(self, 'Warning', 'No thumbnail file. Please create one.')

    def publish(self):

        prepub = None
        heropub = None
        sgpub = None

        version_status = 'apr'
        task_status = 'fin'
        resolution = self.check_task_resolution()
        
        self.get_message()

        try:

            for res in resolution:
                version_res = '_'.join([self.asset_name,self.department,res,self.version])

                self.trace('Export Resource Files')
                prepub = pub_utils.create_asset_pre_publish(self.this_path, self.department, res)
                self.trace('Copy Resource Files to \"lib\"')
                heropub = pub_utils.copy_asset_hero(self.this_path, self.department, res)
                self.trace('Update \"%s\" Version' %(version_res))
                sgpub = pub_utils.set_sg_version(version_res,version_status)
                
            self.trace('Copy Media to Publish Folder')
            if self.thumbnail:
                pub_utils.copy_media_version(self.image_prod,self.image_publ,self.version_name)
            if self.movie:
                pub_utils.copy_media_version(self.movie_prod,self.movie_publ,self.version_name)
            
            self.trace('Update \"Final\" Status on Shotgun')
            pub_utils.set_sg_status(self.sg_tasks,'fin')

            self.trace('Publish Completed!!')
            QtGui.QMessageBox.information(self, 'Information', 'Publish Completed!!')

        except TypeError as exc:

            if not sg_wrapper.get_version_entity(version_res):
                QtGui.QMessageBox.information(self, 'Error', 'No \"%s\" Exists on shotgun.\nPlease match your version' %(version_res))

            else:
                print 'TypeError : ' , exc
                print 'Resource Files' , prepub
                print 'Lib Hero' , heropub
                print 'Shotgun Update' , sgpub

                QtGui.QMessageBox.information(self, 'Error', 'Please Check in Script Editor.\nTypeError : %s' %(exc))

