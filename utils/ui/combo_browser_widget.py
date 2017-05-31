import sys
import os
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets


class ProjectBrowser(QtWidgets.QWidget) :
    entityChanged = QtCore.Signal(list)
    def __init__(self, parent=None, root=None, mode='asset', pathInfo=None) :
        super(ProjectBrowser, self).__init__(parent)
        self.allLayout = QtWidgets.QGridLayout()

        # root
        self.root = root
        self.mode = mode

        self.pathInfo = pathInfo

        # label
        self.projectLabel = QtWidgets.QLabel()
        self.entitySub1Label = QtWidgets.QLabel()
        self.entitySub2Label = QtWidgets.QLabel()
        self.entityLabel = QtWidgets.QLabel()
        self.taskLabel = QtWidgets.QLabel()

        # comboBox
        self.projectComboBox = QtWidgets.QComboBox()
        self.entitySub1ComboBox = QtWidgets.QComboBox()
        self.entitySub2ComboBox = QtWidgets.QComboBox()
        self.entityComboBox = QtWidgets.QComboBox()
        self.taskComboBox = QtWidgets.QComboBox()

        self.allLayout.addWidget(self.projectLabel, 0, 0)
        self.allLayout.addWidget(self.projectComboBox, 0, 1)

        self.allLayout.addWidget(self.entitySub1Label, 1, 0)
        self.allLayout.addWidget(self.entitySub1ComboBox, 1, 1)

        self.allLayout.addWidget(self.entitySub2Label, 2, 0)
        self.allLayout.addWidget(self.entitySub2ComboBox, 2, 1)

        self.allLayout.addWidget(self.entityLabel, 3, 0)
        self.allLayout.addWidget(self.entityComboBox, 3, 1)

        self.allLayout.setColumnStretch(1, 2)
        self.allLayout.setSpacing(8)

        self.setLayout(self.allLayout)

        self.set_label(mode=self.mode)
        self.set_signals()

    def set_label(self, mode):
        """ set label for asset / scene """
        self.projectLabel.setText('Project : ')
        self.taskLabel.setText('Task : ')

        if mode == 'asset':
            self.entitySub1Label.setText('Type : ')
            self.entitySub2Label.setText('SubType : ')
            self.entityLabel.setText('Asset : ')

        if mode == 'scene':
            self.entitySub1Label.setText('Episode : ')
            self.entitySub2Label.setText('Sequence : ')
            self.entityLabel.setText('Shot : ')


    def set_signals(self):
        """ init signals for widgets """
        self.projectComboBox.currentIndexChanged.connect(self.set_entitysub1)
        self.entitySub1ComboBox.currentIndexChanged.connect(self.set_entitysub2)
        self.entitySub2ComboBox.currentIndexChanged.connect(self.set_entity)
        self.entityComboBox.currentIndexChanged.connect(self.call_back)


    def browsing(self):
        self.set_project()
        self.set_match() # only work with Maya

    def set_project(self):
        if self.root:
            projects = listFolder(self.root)
            self.projectComboBox.clear()
            self.entitySub1ComboBox.clear()
            self.entitySub2ComboBox.clear()
            self.entityComboBox.clear()

            if projects:
                self.projectComboBox.addItems(projects)


    def set_entitysub1(self):
        if self.root and str(self.projectComboBox.currentText()):
            path = ('/').join([self.root, str(self.projectComboBox.currentText()), self.mode])
            dirs = listFolder(path)
            self.entitySub1ComboBox.clear()
            self.entitySub2ComboBox.clear()
            self.entityComboBox.clear()

            if dirs:
                self.entitySub1ComboBox.addItems(dirs)

    def set_entitysub2(self):
        if self.root and str(self.projectComboBox.currentText()) and str(self.entitySub1ComboBox.currentText()):
            path = ('/').join([self.root, str(self.projectComboBox.currentText()), self.mode, str(self.entitySub1ComboBox.currentText())])
            dirs = listFolder(path)
            self.entitySub2ComboBox.clear()
            self.entityComboBox.clear()

            if dirs:
                self.entitySub2ComboBox.addItems(dirs)

    def set_entity(self):
        """ set entity comboBox """
        if self.root and str(self.projectComboBox.currentText()) and str(self.entitySub1ComboBox.currentText()) and str(self.entitySub2ComboBox.currentText()):
            path = ('/').join([self.root, str(self.projectComboBox.currentText()), self.mode, str(self.entitySub1ComboBox.currentText()), str(self.entitySub2ComboBox.currentText())])
            dirs = listFolder(path)
            self.entityComboBox.clear()

            if dirs:
                self.entityComboBox.addItems(dirs)


    def call_back(self):
        """ call_back """
        project = str(self.projectComboBox.currentText())
        entitySub1 = str(self.entitySub1ComboBox.currentText())
        entitySub2 = str(self.entitySub2ComboBox.currentText())
        entity = str(self.entityComboBox.currentText())

        self.entityChanged.emit([project, entitySub1, entitySub2, entity])

    def path(self):
        """ return path from all combinations """
        if self.root and str(self.projectComboBox.currentText()) and str(self.entitySub1ComboBox.currentText()) and str(self.entitySub2ComboBox.currentText()):
            path = ('/').join([self.root,
                                str(self.projectComboBox.currentText()),
                                self.mode,
                                str(self.entitySub1ComboBox.currentText()),
                                str(self.entitySub2ComboBox.currentText()),
                                str(self.entityComboBox.currentText())]
                                )
            return path

    def set_match(self):
        """ set comboBox to match open scene path in Maya """
        if self.pathInfo.path:
            project = self.pathInfo.project

            if self.mode == 'asset':
                entitySub1 = self.pathInfo.type
                entitySub2 = self.pathInfo.subtype

            if self.mode == 'scene':
                entitySub1 = self.pathInfo.episode
                entitySub2 = self.pathInfo.sequence

            entity = self.pathInfo.name

            self.entityComboBox.blockSignals(True)

            ''' project '''
            projects = [self.projectComboBox.itemText(i) for i in range(self.projectComboBox.count())]

            if project in projects:
                self.projectComboBox.setCurrentIndex(projects.index(project))

            '''entitySub1'''
            entitiesSub1 = [self.entitySub1ComboBox.itemText(i) for i in range(self.entitySub1ComboBox.count())]

            if entitySub1 in entitiesSub1:
                self.entitySub1ComboBox.setCurrentIndex(entitiesSub1.index(entitySub1))

            '''entitySub2'''
            entitiesSub2 = [self.entitySub2ComboBox.itemText(i) for i in range(self.entitySub2ComboBox.count())]

            if entitySub2 in entitiesSub2:
                self.entitySub2ComboBox.setCurrentIndex(entitiesSub2.index(entitySub2))

            '''entity'''
            entities = [self.entityComboBox.itemText(i) for i in range(self.entityComboBox.count())]

            if entity in entities:
                self.entityComboBox.setCurrentIndex(entities.index(entity))

            self.entityComboBox.blockSignals(False)
            self.call_back()

    def enable(self, state):
        self.projectComboBox.setEnabled(state)
        self.entitySub1ComboBox.setEnabled(state)
        self.entitySub2ComboBox.setEnabled(state)
        self.entityComboBox.setEnabled(state)



def listFolder(path=''):
    """ list folder """
    dirs = []
    if os.path.exists(path):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]