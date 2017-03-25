import os
import sys
from PySide import QtCore
from PySide import QtGui
import status_config
from rftool.utils import sg_process

class StatusWidget(QtGui.QWidget) :
    def __init__(self, parent = None) :
        super(StatusWidget, self).__init__(parent)
        self.allLayout = QtGui.QVBoxLayout()
        self.widget = QtGui.QComboBox()
        self.allLayout.addWidget(self.widget)
        self.allLayout.setSpacing(0)
        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

    def set_task_status(self, limit=None):
        self.widget.clear()
        statusOrder = status_config.statusOrder

        # set limit status
        if limit:
            statusOrder = [a for a in status_config.statusOrder if a in limit]

        # fill status
        for i, status in enumerate(statusOrder):
            statusDict = status_config.statusMap[status]
            iconPath = statusDict.get('icon')
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(iconPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)

            self.widget.addItem(statusDict.get('display'))
            self.widget.setItemIcon(i, icon)
            self.widget.setItemData(i, status, QtCore.Qt.UserRole)


class TaskWidget(QtGui.QWidget) :
    def __init__(self, parent=None) :
        super(TaskWidget, self).__init__(parent)
        self.allLayout = QtGui.QVBoxLayout()
        self.widget = QtGui.QComboBox()
        self.allLayout.addWidget(self.widget)
        self.allLayout.setSpacing(0)
        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

        self.caches = dict()

    def set_task_status(self, mode, project, entity, filter1=str(), filter2=str(), step=None):
        self.widget.clear()
        filters = []
        fields = ['content', 'entity', 'id', 'sg_status_list']

        if mode == 'asset':
            filters = [['project.Project.name', 'is', project], ['entity.Asset.code', 'is', entity]]

            if filter1:
                filters.append(['entity.Asset.sg_type', 'is', filter1])

            if filter2:
                filters.append(['entity.Asset.sg_subtype', 'is', filter2])

            if step:
                if type(step) == type(dict()):
                    filters.append(['step', 'is', step])

                if type(step) == type(str()):
                    filters.append(['step.Step.code', 'is', step])

            key = '%s-%s-%s-%s-%s' % (project, filter1, filter2, entity, str(step))

            if not key in self.caches.keys():
                tasks = sg_process.sg.find('Task', filters, fields)
                self.caches.update({key: tasks})
            else:
                tasks = self.caches[key]

            if tasks:
                for task in tasks:
                    self.widget.addItem(task.get('content'))


class UserWidget(QtGui.QWidget) :
    def __init__(self, parent = None) :
        super(UserWidget, self).__init__(parent)
        self.allLayout = QtGui.QVBoxLayout()
        self.widget = QtGui.QComboBox()
        self.allLayout.addWidget(self.widget)
        self.allLayout.setSpacing(0)
        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

        # temp dir
        self.userFile = '%s/sgUser' % os.environ.get('temp')

        self.set_users()
        self.widget.currentIndexChanged.connect(self.save)

    def set_users(self):
        """ set sg users """
        self.widget.clear()
        fields = ['name', 'id']
        users = sg_process.sg.find('HumanUser', [], fields)
        data = None
        activeRow = 0

        data = self.read()

        for row, user in enumerate(sorted(users)):
            self.widget.addItem(user.get('name'))
            self.widget.setItemData(row, user, QtCore.Qt.UserRole)

            if data:
                if user.get('name') == data.get('name'):
                    activeRow = row

        self.widget.setCurrentIndex(activeRow)

    def save(self):
        """ save when item changed """
        user = self.widget.itemData(self.widget.currentIndex(), QtCore.Qt.UserRole)
        self.write(str(user))

    def read(self):
        """ read saved user data """
        if os.path.exists(self.userFile):
            f = open(self.userFile, 'r')
            data = eval(f.read())
            f.close()

            return data

    def write(self, data):
        """ write user data """
        f = open(self.userFile, 'w')
        f.write(data)
        f.close()

class StepWidget(QtGui.QWidget) :
    """ department comboBox """
    def __init__(self, parent=None, pathInfo=None) :
        super(StepWidget, self).__init__(parent)
        self.pathInfo = pathInfo
        self.allLayout = QtGui.QVBoxLayout()
        self.widget = QtGui.QComboBox()
        self.allLayout.addWidget(self.widget)
        self.allLayout.setSpacing(0)
        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

    def list_steps(self, entityType='Asset'):
        fields = ['id', 'code', 'entity_type']
        filters = [['entity_type', 'is', entityType]]
        allSteps = sg_process.sg.find('Step', filters, fields)

        self.widget.clear()
        steps = [a for a in allSteps if a.get('code') in status_config.stepLimit.get(entityType)]

        for row, step in enumerate(sorted(steps)):
            self.widget.addItem(step.get('code'))
            self.widget.setItemData(row, step, QtCore.Qt.UserRole)

        if self.pathInfo.path:
            stepList = [str(self.widget.itemText(a)).lower() for a in range(self.widget.count())]

            if self.pathInfo.step in stepList:
                self.widget.setCurrentIndex(stepList.index(self.pathInfo.step))

    def step(self):
        """ get current step """
        return self.widget.itemData(self.widget.currentIndex(), QtCore.Qt.UserRole)

    def enable(self, state):
        self.widget.setEnabled(state)
