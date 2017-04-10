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
    uiName = 'scene_publish_UI'
    deleteUI(uiName)
    myApp = ScenePublish(getMayaWindow())
    # myApp.show()

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

class ScenePublish(QtGui.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(ScenePublish, self).__init__(parent)

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
        self.main_styleSheet = 'QPushButton {\n    background-color: rgb(100, 200, 0);\n    border-style: inset;\n    border-width: 1px;\n    border-radius: 6px;\n    border-color: rgb(10, 90, 0);\n    font: bold 12px;\n}\nQPushButton:pressed {\n    background-color: rgb(15, 125, 15);\n}'
        self.sub_styleSheet = 'QPushButton {\n    background-color: rgb(255, 100, 0);\n    border-style: inset;\n    border-width: 1px;\n    border-radius: 6px;\n    border-color: rgb(100, 25, 0);\n    font: bold 11px;\n}\nQPushButton:pressed {\n    background-color: rgb(20, 20, 20);\n}'
        self.none_styleSheet = 'QPushButton {\n    background-color: rgb(115, 115, 115);\n    border-style: inset;\n    border-width: 1px;\n    border-radius: 6px;\n    border-color: rgb(100,25, 0);\n    font: bold 11px;\n}\nQPushButton:pressed {\n    background-color: rgb(160, 160, 160);\n}'

        self.get_scene_info()
        self.get_sg_info()
        self.get_media_info()

        self.set_ui_information()

    def init_connect(self):
        self.ui.playblast_pushButton.clicked.connect(self.playblast)
        self.ui.review_pushButton.clicked.connect(self.review)
        self.ui.publish_pushButton.clicked.connect(self.publish)

    def trace(self,status):
        self.ui.status_label.setText(status)
        QtGui.QApplication.processEvents()

    def get_scene_info(self):
        self.scene = path_info.PathInfo()
        self.this_path = self.scene.path
        self.project = self.scene.project
        self.version = file_utils.find_version(self.this_path)
        # self.version_name = self.scene.name + 
        self.episode = self.scene.episode
        self.sequence = self.scene.sequence
        self.shot = self.scene.shot
        self.department = self.scene.step
        self.version_name = '_'.join(self.scene.fileUser.split('_')[:-1])
        self.user_name = self.scene.user

        self.prod_dir = self.scene.entityPath(root='RFPROD')
        self.prod_avi = self.prod_dir + '/movies/' + self.version_name + '.avi'
        self.prod_mov = self.prod_dir + '/movies/' + self.version_name + '.mov'
        self.prod_img = self.prod_dir + '/images/' + self.version_name + '.jpg'

        self.thumbnails = None
        self.movies = None

    def get_sg_info(self):
        self.sg_scene = sg_process.get_one_shot(self.project, self.episode, self.sequence, self.shot)
        self.sg_task = sg_process.get_one_task(self.sg_scene,self.department)
        self.sg_version = sg_process.get_one_version(self.version_name)

    def get_media_info(self):
        self.thumbnails = [ os.path.dirname(self.prod_img) + '/%s' %(n) for n in file_utils.listFile(os.path.dirname(self.prod_img)) if self.version in n ]
        self.movies = [ os.path.dirname(self.prod_avi) + '/%s' %(n) for n in file_utils.listFile(os.path.dirname(self.prod_avi)) if self.version in n ]

        if not self.thumbnails == None and not self.movies == None:
            self.trace('Media Exists. Ready for submit/publish.')

        if self.sg_version and self.sg_version['sg_status_list'] == 'rev':
            self.ui.publish_pushButton.setStyleSheet(self.main_styleSheet)
            self.ui.publish_pushButton.setEnabled(True)
        if not self.sg_version or not self.sg_version['sg_status_list'] == 'rev':
            self.ui.publish_pushButton.setStyleSheet(self.none_styleSheet)
            self.ui.publish_pushButton.setEnabled(False)


    def set_ui_information(self):
        self.ui.version_lineEdit.setText(self.version_name)
        self.ui.episode_lineEdit.setText(self.episode)
        self.ui.sequence_lineEdit.setText(self.sequence)
        self.ui.shot_lineEdit.setText(self.shot)
        self.ui.department_lineEdit.setText(self.department)

    def playblast(self):
        index = int(self.ui.playblast_res_comboBox.currentIndex())

        if index == 0:
            res = 100
        if index == 1:
            res = 50
        if index == 2:
            res = 25

        scene = pub_utils.layout_pub(self.this_path,res)
        self.thumbnails, self.movies, chks = scene.playblast_all()

        if False in chks:
            QtGui.QMessageBox.warning(self, 'Warning', 'Uncorrectly camera name or start time or end time\nPlease check at camera.')

    def review(self):
        version_status = 'rev'
        task_status = 'rev'
        message = str(self.ui.message_plainTextEdit.toPlainText())

        self.trace('Submitting...')
        print self.thumbnails
        print self.movies

        if type(self.thumbnails) is list and not (None in self.thumbnails) and type(self.movies) is list and not (None in self.movies):

            pub_utils.create_sg_version(self.project, self.sg_scene, self.version_name, self.sg_task, version_status ,self.thumbnails[0], message, self.movies[0])
            self.trace('Create version on shotgun')

            pub_utils.set_sg_status([self.sg_task],task_status)
            self.trace('Set "Pending for review" status on task')

            increment = pub_utils.create_increment_work_file(self.this_path)
            self.trace('Save as increment version')

        if self.thumbnails is str() and self.movies is str():
            pub_utils.create_sg_version(self.project, self.sg_scene, self.version_name, self.sg_task, version_status ,self.thumbnails, message, self.movies)
            self.trace('Create version on shotgun')
            pub_utils.set_sg_status([self.sg_task],task_status)
            self.trace('Set status on task')

            increment = pub_utils.create_increment_work_file(self.this_path)
            self.trace('Save as increment version')

        else:
            QtGui.QMessageBox.warning(self, 'Warning', 'Please get new playblast.')

    def publish(self):
        version_status = 'apr'
        task_status = 'fin'
        message = str(self.ui.message_plainTextEdit.toPlainText())
        check = False

        self.trace('Publishing...')

        print self.sg_task['sg_status_list'], task_status

        # if not self.sg_task['sg_status_list'] == task_status:

        #     QtGui.QMessageBox.warning(self, 'Warning', 'This version was published. Are you sure for publish this version?', )

            # if type(self.thumbnails) is list and not (None in self.thumbnails) and type(self.movies) is list and not (None in self.movies):

            #     pub_utils.set_sg_version(self.version_name, version_status)
            #     self.trace('Create version on shotgun')

            #     pub_utils.set_sg_status([self.sg_task],task_status)
            #     self.trace('Set "Pending for review" status on task')

            # if self.thumbnails is str() and self.movies is str():
            #     pub_utils.set_sg_version(self.version_name, version_status)
            #     self.trace('Create version on shotgun')
            #     pub_utils.set_sg_status([self.sg_task],task_status)
            #     self.trace('Set status on task')

            # else:
            #     QtGui.QMessageBox.warning(self, 'Warning', 'Please get new playblast.')

class FrameConfirmWindow(QtGui.QMainWindow):
    """docstring for FrameConfirmWidget"""
    def __init__(self, parent=None):
        super(FrameConfirmWindow, self).__init__()

        self.headers = ['Shot Name',' Start ','  End  ','Duration']
        
        self.shot_table = QtGui.QTableWidget()

        self.shot_table.setColumnCount(4)
        self.shot_table.setHorizontalHeaderLabels(self.headers)
        self.shot_table.setSelectionMode(QtCore.Qt.NoSelection)

        self.show()

    def setRows(self,shotLists=dict()):

        # { 's0010' : { 'start' : 101 , 'end' : 136 , 'duration' : 36 },
        #   's0020' : { 'start' : 201 , 'end' : 289 , 'duration' : 89 }}

        shots = shotLists.keys()
        shots.sort()

        row = 0
        rows = len(shots)

        self.shot_table.setRowCount(rows)

        for shot in shots:

            shot_name = shot
            shot_start = shotLists[shot]['start']
            shot_end = shotLists[shot]['end']
            shot_duration = shotLists[shot]['duration']

            shot_item = QtGui.QTableWidgetItem(shot)
            sta_item = QtGui.QTableWidgetItem(shot_start)
            end_item = QtGui.QTableWidgetItem(shot_end)
            dur_item = QtGui.QTableWidgetItem(shot_duration)

            self.shot_table.setItem(row,0,shot_item)
            self.shot_table.setItem(row,1,sta_item)
            self.shot_table.setItem(row,2,end_item)
            self.shot_table.setItem(row,3,dur_item)

            row += 1







        