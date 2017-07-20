import os
import sys
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

module_path = sys.modules[__name__].__file__
module_dir  = os.path.dirname(module_path)

import status_config
from rftool.utils import sg_process
from rftool.utils import icon
import grab_screen
import tempfile

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class StatusWidget(QtWidgets.QWidget) :
    def __init__(self, parent = None) :
        super(StatusWidget, self).__init__(parent)
        self.allLayout = QtWidgets.QVBoxLayout()
        self.widget = QtWidgets.QComboBox()
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

    def get_task_status(self): 
        itemData = self.widget.itemData(self.widget.currentIndex(), QtCore.Qt.UserRole)
        return itemData



class TaskWidget(QtWidgets.QWidget) :
    def __init__(self, parent=None) :
        super(TaskWidget, self).__init__(parent)
        self.allLayout = QtWidgets.QVBoxLayout()
        self.widget = QtWidgets.QComboBox()
        self.allLayout.addWidget(self.widget)
        self.allLayout.setSpacing(0)
        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

        self.caches = dict()

    def set_task(self, mode, project, entity, filter1=str(), filter2=str(), step=None, setBlank=True):
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

            # cache area
            if not key in self.caches.keys():
                tasks = sg_process.sg.find('Task', filters, fields)
                self.caches.update({key: tasks})
            else:
                tasks = self.caches[key]

            if tasks:
                firstItem = 0
                if setBlank:
                    self.widget.addItem('- Select Task -')
                    firstItem = 1

                for row, task in enumerate(tasks):
                    self.widget.addItem(task.get('content'))
                    self.widget.setItemData((row+firstItem), task, QtCore.Qt.UserRole)

    def get_task(self): 
        itemData = self.widget.itemData(self.widget.currentIndex(), QtCore.Qt.UserRole)
        return itemData



class UserWidget(QtWidgets.QWidget) :
    def __init__(self, parent = None) :
        super(UserWidget, self).__init__(parent)
        self.allLayout = QtWidgets.QVBoxLayout()
        self.widget = QtWidgets.QComboBox()
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

class StepWidget(QtWidgets.QWidget) :
    """ department comboBox """
    def __init__(self, parent=None, pathInfo=None) :
        super(StepWidget, self).__init__(parent)
        self.pathInfo = pathInfo
        self.allLayout = QtWidgets.QVBoxLayout()
        self.widget = QtWidgets.QComboBox()
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

class DropUrlListWidget(QtWidgets.QListWidget):
    """ subclass QListWidget for dragdrop events """
    dropped = QtCore.Signal(list)
    def __init__(self, parent=None):
        super(DropUrlListWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QtCore.QSize(72, 72))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.dropped.emit(links)
        else:
            event.ignore()

class SnapImageWidget(QtWidgets.QWidget) :
    """ department comboBox """
    itemClicked = QtCore.Signal(str)
    def __init__(self, formats, isMaya, imgDst=None, parent=None) :
        super(SnapImageWidget, self).__init__(parent)
        self.allLayout = QtWidgets.QVBoxLayout()
        self.widget = DropUrlListWidget()
        self.button = QtWidgets.QPushButton()
        self.allLayout.addWidget(self.widget)
        self.allLayout.addWidget(self.button)
        self.allLayout.setSpacing(2)
        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

        self.formats = formats

        self.preCapScreen = DimScreen(isMaya=isMaya, dstDir=imgDst)
        self.button.setText('Snap Screen')

        self.widget.dropped.connect(self.display)
        self.widget.itemSelectionChanged.connect(self.call_back)

    def display(self, urls):
        """ display path """
        for url in urls:
            if os.path.splitext(url)[-1] in self.formats:
                item = QtWidgets.QListWidgetItem(self.widget)
                item.setText(os.path.basename(url))
                item.setData(QtCore.Qt.UserRole, url)
                self.widget.setCurrentItem(item)

            else:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Please drop only %s file' % str(self.formats))

    def call_back(self):
        item = self.widget.currentItem()
        data = item.data(QtCore.Qt.UserRole)
        self.itemClicked.emit(data)


class SnapImageMayaWidget(QtWidgets.QWidget) :
    """ department comboBox """
    itemClicked = QtCore.Signal(str)
    snapped = QtCore.Signal(str)


    def __init__(self, formats, snapFormat, imgDst=None, parent=None) :
        super(SnapImageMayaWidget, self).__init__(parent)
        self.allLayout = QtWidgets.QVBoxLayout()

        self.widget = DropUrlListWidget()
        self.widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.button = QtWidgets.QPushButton()
        self.allLayout.addWidget(self.widget)
        self.allLayout.addWidget(self.button)
        self.allLayout.setSpacing(2)
        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

        self.formats = formats
        self.snapFormat = snapFormat

        self.button.setText('Snap Screen')

        self.widget.dropped.connect(self.display)
        self.widget.itemSelectionChanged.connect(self.call_back)
        self.button.clicked.connect(self.snap)
        self.widget.customContextMenuRequested.connect(self.context_menu)

    def display(self, urls):
        """ display path """
        for url in urls:
            if os.path.splitext(url)[-1] in self.formats:
                item = QtWidgets.QListWidgetItem(self.widget)
                item.setText(os.path.basename(url))
                item.setData(QtCore.Qt.UserRole, url)
                self.widget.setCurrentItem(item)

            else:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Please drop only %s file' % str(self.formats))

    def call_back(self):
        item = self.widget.currentItem()
        data = icon.nopreview

        if item: 
            data = item.data(QtCore.Qt.UserRole)
        
        self.itemClicked.emit(data)

    def snap(self): 
        tempDir = tempfile.gettempdir()
        from rftool.utils import maya_utils
        dst = self.snap_sequence()
        format = self.snapFormat
        st = maya_utils.mc.currentTime(q=True)
        sequencer = False
        w = 1280
        h = 1024

        maya_utils.capture_screen(dst, format, st, sequencer, w, h)
        logger.debug('snapped %s' % dst)
        self.display([dst])
        # self.snapped.emit(dst)

    def snap_sequence(self): 
        tempDir = tempfile.gettempdir()

        if self.widget.count() > 0: 
            filenames = [str(self.widget.item(row).text()) for row in range(self.widget.count())]
            versions = [int(a.split('_')[-1].split('.')[0]) for a in filenames]
            nextVersion = sorted(versions)[-1] + 1
            snapName = 'snap_%03d.%s' % (nextVersion, self.snapFormat)

        else: 
            snapName = 'snap_001.%s' % self.snapFormat

        snapPath = '%s/%s' % (tempDir, snapName)
        return snapPath


    def context_menu(self, pos): 
        menu = QtWidgets.QMenu(self)
        currentItem = self.widget.currentItem()

        if currentItem:
            # basic menu 
            itemAction = menu.addAction('Remove')
            itemAction.triggered.connect(self.remove_item)
        
        defaultAction = menu.addAction('Clear All')
        defaultAction.triggered.connect(self.remove_all_items)

        menu.popup(self.widget.mapToGlobal(pos))

    def remove_item(self): 
        self.widget.takeItem(self.widget.currentRow())

    def remove_all_items(self): 
        self.widget.clear()
        self.call_back()

    def get_all_items(self): 
        items = [self.widget.item(a) for a in range(self.widget.count())]
        return items

    def get_all_paths(self): 
        items = [a.data(QtCore.Qt.UserRole) for a in self.get_all_items()]
        return items


class SnapSingleImageWidget(QtWidgets.QWidget) :
    """ department comboBox """
    snapped = QtCore.Signal(str)
    def __init__(self, isMaya, imgDst=None, parent=None) :
        super(SnapSingleImageWidget, self).__init__(parent=parent)
        self.allLayout = QtWidgets.QVBoxLayout()

        self.previewLabel = QtWidgets.QLabel()
        self.button = QtWidgets.QPushButton()

        self.allLayout.addWidget(self.previewLabel)
        self.allLayout.addWidget(self.button)
        self.allLayout.setSpacing(2)
        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

        self.preCapScreen = DimScreen(isMaya=isMaya, dstDir=imgDst)
        self.button.setText('Snap Screen')

        self.w = 300
        self.h = 200
        iconPath = '%s/_sgicons/nopreview_300_200.png' % (module_dir)
        self.previewLabel.setPixmap(QtGui.QPixmap(iconPath).scaled(self.w, self.h, QtCore.Qt.KeepAspectRatio))

        self.preCapScreen.snapped.connect(self.preview)
        self.button.clicked.connect(self.snap)
        self.previewFile = str()


    def snap(self):
        """ display path """
        self.preCapScreen.show()

    def preview(self, img):
        self.previewLabel.setPixmap(QtGui.QPixmap(img).scaled(self.w, self.h, QtCore.Qt.KeepAspectRatio))
        self.previewFile = img
        self.snapped.emit(img)


class PublishListWidget(QtWidgets.QWidget) :
    """ custom listwidget for publish """
    currentItemChanged = QtCore.Signal(object)


    def __init__(self, parent=None) :
        super(PublishListWidget, self).__init__(parent)
        self.allLayout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel()
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.currentItemChanged.connect(self.call_back)

        self.allLayout.addWidget(self.label)
        self.allLayout.addWidget(self.listWidget)
        self.allLayout.setSpacing(2)
        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

    def add_item(self, display, description=None, data=None, iconPath=None, checkStateEnable=True): 
        item = QtWidgets.QListWidgetItem(self.listWidget)
        itemWidget = PublishListWidgetItem()
        itemWidget.set_text(display)

        if description: 
            itemWidget.set_description(description)

        if data: 
            item.setData(QtCore.Qt.UserRole, data)

        if iconPath: 
            iconWidget = QtGui.QIcon()
            iconWidget.addPixmap(QtGui.QPixmap(iconPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(iconWidget)

        itemWidget.set_check_state(checkStateEnable)


        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, itemWidget)
        item.setSizeHint(itemWidget.sizeHint())

        return item 

    def set_item_status(self, item, status): 
        widget = self.listWidget.itemWidget(item)
        
        if status == 'ready': 
            widget.set_movie(icon.gear)
            widget.start_movie()
            widget.stop_movie()

        if status == 'ip': 
            widget.set_movie(icon.gear)
            widget.start_movie()

        if status == True: 
            widget.set_movie(icon.success)
            widget.start_movie()

        if status == False or not status: 
            widget.set_movie(icon.failed)
            widget.start_movie()


    def call_back(self, item): 
        self.currentItemChanged.emit(item)


class PublishListWidgetItem(QtWidgets.QWidget) :
    def __init__(self, parent = None) :
        super(PublishListWidgetItem, self).__init__(parent)
        # set label
        self.allLayout = QtWidgets.QHBoxLayout()
        self.textLabel = QtWidgets.QLabel()
        self.descriptionLabel = QtWidgets.QLabel()
        self.descriptionLabel.setStyleSheet('color: rgb(%s, %s, %s);' % (100, 100, 100))

        # checkBox 
        self.checkBox = QtWidgets.QCheckBox()
        self.checkBox.setCheckState(QtCore.Qt.Checked)

        # set icon
        self.iconQLabel = QtWidgets.QLabel()

        self.spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.allLayout.addWidget(self.checkBox, 0, 0)
        self.allLayout.addWidget(self.iconQLabel, 0, 1)
        self.allLayout.addWidget(self.textLabel, 0, 2)
        self.allLayout.addWidget(self.descriptionLabel, 2, 3)
        self.allLayout.addItem(self.spacerItem)

        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

        # set font 
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.descriptionLabel.setFont(font)


    def set_text(self, text) :
        self.textLabel.setText(text)

    def set_description(self, text) :
        self.descriptionLabel.setText(text)

    def set_icon(self, iconPath, size = 16) :
        self.iconQLabel.setPixmap(QtGui.QPixmap(iconPath).scaled(size, size, QtCore.Qt.KeepAspectRatio))

    def set_movie(self, iconPath): 
        movie = QtGui.QMovie(iconPath)
        self.iconQLabel.setMovie(movie)
        movie.start()
        movie.stop()

    def set_text_color(self, color) :
        self.textLabel.setStyleSheet('color: rgb(%s, %s, %s);' % (color[0], color[1], color[2]))

    def text(self) :
        return self.textLabel.text()

    def description(self) :
        return self.descriptionLabel.text()

    def start_movie(self): 
        movie = self.iconQLabel.movie()
        movie.start()

    def stop_movie(self): 
        movie = self.iconQLabel.movie()
        movie.stop()

    def set_check(self, state): 
        if state: 
            self.checkBox.setCheckState(QtCore.Qt.Checked)

        else: 
            self.checkBox.setCheckState(QtCore.Qt.UnChecked)

    def get_checked_state(self): 
        return self.checkBox.isChecked()

    def set_check_state(self, state): 
        self.checkBox.setEnabled(state)



class DropUrlLineEdit(QtWidgets.QLineEdit):
    """ subclass QLineEdit for dragdrop events """
    dropped = QtCore.Signal(list)
    def __init__(self, parent=None):
        super(DropUrlLineEdit, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.dropped.emit(links)
        else:
            event.ignore()

class DropPathWidget(QtWidgets.QWidget) :
    """ lineEdit drag drop Widget """
    textChanged = QtCore.Signal(str)
    def __init__(self, parent=None) :
        super(DropPathWidget, self).__init__(parent)
        self.allLayout = QtWidgets.QVBoxLayout()
        self.widget = DropUrlLineEdit()
        self.allLayout.addWidget(self.widget)
        self.allLayout.setSpacing(0)
        self.allLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.allLayout)

        self.widget.dropped.connect(self.call_back)

    def call_back(self, urls):
        """ display path """
        self.widget.setText(urls[0])
        self.textChanged.emit(urls[0])


class DimScreen(QtWidgets.QSplashScreen):
    snapped = QtCore.Signal(str)
    """ snap screen shot with rubber band """
    """ darken the screen by making splashScreen """
    # app = QtWidgets.QApplication.instance() -> for maya
    # app = QtWidgets.QApplication(sys.argv) -> for standalone

    def __init__(self, isMaya, dstDir=None, filename=None, ext='png'):
        """"""
        if isMaya:
            app = QtWidgets.QApplication.instance()
        else:
            app = QtWidgets.QApplication.instance()
            if not app: 
                app = QtWidgets.QApplication(sys.argv)

        screenGeo = app.desktop().screenGeometry()
        width = screenGeo.width()
        height = screenGeo.height()
        fillPix = QtGui.QPixmap(width, height)
        fillPix.fill(QtGui.QColor(1,1,1))

        super(DimScreen, self).__init__(fillPix)
        self.havePressed = False
        self.origin = QtCore.QPoint(0,0)
        self.end = QtCore.QPoint(0,0)
        self.rubberBand = None


        self.setWindowState(QtCore.Qt.WindowFullScreen)
        #self.setBackgroundRole(QtWidgets.QPalette.Dark)
        self.setWindowOpacity(0.4)

        self.dstDir = self.setImgDst(dstDir)
        self.filename = filename
        self.ext = ext



    def mousePressEvent(self, event):
        self.havePressed = True
        self.origin = event.pos()

        if not self.rubberBand:
            self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.rubberBand.hide()
        if self.havePressed == True:
            self.end = event.pos()
            self.hide()

            output = self.capture()

    def capture(self):
        outputFile = self.output()
        QtGui.QPixmap.grabWindow(QtWidgets.QApplication.desktop().winId(), self.origin.x(), self.origin.y(), self.end.x()-self.origin.x(), self.end.y()-self.origin.y()).save(outputFile, self.ext)
        self.snapped.emit(outputFile)
        logger.info(outputFile)
        return outputFile


    def output(self):
        return '%s/tmpSnap.%s' % (self.dstDir, self.ext)
    # def setOutput(self):
    #     files = listFile(self.dstDir)

    #     if files:
    #         os.remove()



    def setImgDst(self, dstDir):
        if not dstDir:
            dstDir = '%s/pipelineWidgetCaptureTmp' % os.environ['TEMP']

        if not os.path.exists(dstDir):
            os.makedirs(dstDir)
            logger.debug('Create snap dir %s' % dstDir)

        return dstDir


def listFolder(path=''):
    """ list folder """
    dirs = []
    if os.path.exists(path):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]


def listFile(path=''):
    """ list files """
    return [d for d in os.listdir(path) if os.path.isfile(os.path.join(path, d))]
