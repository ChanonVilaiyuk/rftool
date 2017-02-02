#Import python modules
import sys, os, re, shutil, random

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

#Import GUI
from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

#Import maya commands
import maya.cmds as mc
import maya.mel as mm
from functools import partial

# import ui
import ui_dialog
from rftool.utils import sg_process
from startup import config


class userDialog(QtGui.QDialog):

    def __init__(self, sgUser=None, parent=None):
        super(userDialog, self).__init__(parent)
        self.ui = ui_dialog.Ui_UserDialogUI()
        self.ui.setupUi(self)

        self.sgUser = sgUser
        self.set_signals()
        self.start_check()

    def set_signals(self):
        self.ui.set_pushButton.clicked.connect(self.set_user)
        self.ui.link_pushButton.clicked.connect(self.link_sgUser)

    def start_check(self):
        self.list_sgUser()

        # set local user
        localUser = mc.optionVar(q=config.localUser)
        self.ui.lineEdit.setText(str(localUser))


    def list_sgUser(self):
        if not self.sgUser:
            self.sgUser = sg_process.get_users()
        self.ui.listWidget.clear()
        self.ui.listWidget.setSortingEnabled(True)

        for user in self.sgUser:
            item = QtGui.QListWidgetItem(self.ui.listWidget)

            name = user['name']
            localUser = user['sg_localuser']

            item.setText('%s - %s' % (name, localUser))
            item.setData(QtCore.Qt.UserRole, user)

        self.ui.listWidget.sortItems()

    def set_user(self):
        user = str(self.ui.lineEdit.text())
        mc.optionVar(sv=(config.localUser, user))
        self.ui.set_pushButton.setText('Done')

    def link_sgUser(self):
        item = self.ui.listWidget.currentItem()
        if item:
            userEntitiy = item.data(QtCore.Qt.UserRole)
            sgUser = userEntitiy['name']
            localUser = mc.optionVar(q=config.localUser)

            if not localUser in [a['sg_localuser'] for a in self.sgUser]:
                if not localUser in ['0', 0]:
                    if localUser and sgUser:
                        result = QtGui.QMessageBox.question(self, 'Confirm', 'Link %s to %s?' % (localUser, sgUser), QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)

                        if result == QtGui.QMessageBox.Yes:
                            sg_process.link_local_user(userEntitiy['id'], localUser)
                            self.close()
                else:
                    QtGui.QMessageBox.warning(self, 'Error', 'Please set your name first')
            else:
                QtGui.QMessageBox.warning(self, 'Error', '%s already linked to shotgun account' % localUser)
        else:
            QtGui.QMessageBox.warning(self, 'Error', 'Select shotgun user')
