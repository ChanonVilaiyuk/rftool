# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/TA/Dropbox/script_server/core/maya/rftool/publish/rf_still_publish/ui.ui'
#
# Created: Mon Mar 20 01:10:20 2017
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_StillPublishUI(object):
    def setupUi(self, StillPublishUI):
        StillPublishUI.setObjectName("StillPublishUI")
        StillPublishUI.resize(806, 567)
        self.centralwidget = QtGui.QWidget(StillPublishUI)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.gridLayout_7 = QtGui.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_8 = QtGui.QLabel(self.centralwidget)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_3.addWidget(self.label_8)
        self.source_lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.source_lineEdit.setObjectName("source_lineEdit")
        self.horizontalLayout_3.addWidget(self.source_lineEdit)
        self.gridLayout_7.addLayout(self.horizontalLayout_3, 5, 0, 1, 1)
        self.logo_label = QtGui.QLabel(self.centralwidget)
        self.logo_label.setObjectName("logo_label")
        self.gridLayout_7.addWidget(self.logo_label, 0, 1, 1, 1)
        self.publish_pushButton = QtGui.QPushButton(self.centralwidget)
        self.publish_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.publish_pushButton.setObjectName("publish_pushButton")
        self.gridLayout_7.addWidget(self.publish_pushButton, 9, 0, 2, 1)
        self.publish_listWidget = QtGui.QListWidget(self.centralwidget)
        self.publish_listWidget.setObjectName("publish_listWidget")
        self.gridLayout_7.addWidget(self.publish_listWidget, 6, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.design_radioButton = QtGui.QRadioButton(self.centralwidget)
        self.design_radioButton.setObjectName("design_radioButton")
        self.horizontalLayout.addWidget(self.design_radioButton)
        self.asset_radioButton = QtGui.QRadioButton(self.centralwidget)
        self.asset_radioButton.setChecked(True)
        self.asset_radioButton.setObjectName("asset_radioButton")
        self.horizontalLayout.addWidget(self.asset_radioButton)
        self.scene_radioButton = QtGui.QRadioButton(self.centralwidget)
        self.scene_radioButton.setObjectName("scene_radioButton")
        self.horizontalLayout.addWidget(self.scene_radioButton)
        self.gridLayout_7.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.preview_label = QtGui.QLabel(self.frame)
        self.preview_label.setObjectName("preview_label")
        self.verticalLayout_3.addWidget(self.preview_label)
        self.gridLayout_7.addWidget(self.frame, 1, 1, 6, 1)
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_7.addWidget(self.line, 9, 1, 1, 1)
        self.status_label = QtGui.QLabel(self.centralwidget)
        self.status_label.setObjectName("status_label")
        self.gridLayout_7.addWidget(self.status_label, 10, 1, 1, 1)
        self.line_4 = QtGui.QFrame(self.centralwidget)
        self.line_4.setFrameShape(QtGui.QFrame.HLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout_7.addWidget(self.line_4, 4, 0, 1, 1)
        self.progressBar = QtGui.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout_7.addWidget(self.progressBar, 7, 1, 1, 1)
        self.project_layout = QtGui.QVBoxLayout()
        self.project_layout.setObjectName("project_layout")
        self.mode_label = QtGui.QLabel(self.centralwidget)
        self.mode_label.setObjectName("mode_label")
        self.project_layout.addWidget(self.mode_label)
        self.line_5 = QtGui.QFrame(self.centralwidget)
        self.line_5.setFrameShape(QtGui.QFrame.HLine)
        self.line_5.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.project_layout.addWidget(self.line_5)
        self.department_horizontalLayout = QtGui.QHBoxLayout()
        self.department_horizontalLayout.setObjectName("department_horizontalLayout")
        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.department_horizontalLayout.addWidget(self.label_4)
        self.project_layout.addLayout(self.department_horizontalLayout)
        self.line_2 = QtGui.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.project_layout.addWidget(self.line_2)
        self.projectPlc_frame = QtGui.QFrame(self.centralwidget)
        self.projectPlc_frame.setObjectName("projectPlc_frame")
        self.gridLayout_3 = QtGui.QGridLayout(self.projectPlc_frame)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.entitySub2_comboBox = QtGui.QComboBox(self.projectPlc_frame)
        self.entitySub2_comboBox.setObjectName("entitySub2_comboBox")
        self.gridLayout_3.addWidget(self.entitySub2_comboBox, 2, 1, 1, 1)
        self.project_comboBox = QtGui.QComboBox(self.projectPlc_frame)
        self.project_comboBox.setObjectName("project_comboBox")
        self.gridLayout_3.addWidget(self.project_comboBox, 0, 1, 1, 1)
        self.entitySub1_label = QtGui.QLabel(self.projectPlc_frame)
        self.entitySub1_label.setObjectName("entitySub1_label")
        self.gridLayout_3.addWidget(self.entitySub1_label, 1, 0, 1, 1)
        self.entitySub2_label = QtGui.QLabel(self.projectPlc_frame)
        self.entitySub2_label.setObjectName("entitySub2_label")
        self.gridLayout_3.addWidget(self.entitySub2_label, 2, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.projectPlc_frame)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.entitySub1_comboBox = QtGui.QComboBox(self.projectPlc_frame)
        self.entitySub1_comboBox.setObjectName("entitySub1_comboBox")
        self.gridLayout_3.addWidget(self.entitySub1_comboBox, 1, 1, 1, 1)
        self.entity_label = QtGui.QLabel(self.projectPlc_frame)
        self.entity_label.setObjectName("entity_label")
        self.gridLayout_3.addWidget(self.entity_label, 3, 0, 1, 1)
        self.entity_comboBox = QtGui.QComboBox(self.projectPlc_frame)
        self.entity_comboBox.setObjectName("entity_comboBox")
        self.gridLayout_3.addWidget(self.entity_comboBox, 3, 1, 1, 1)
        self.gridLayout_3.setColumnStretch(0, 1)
        self.project_layout.addWidget(self.projectPlc_frame)
        self.gridLayout_7.addLayout(self.project_layout, 1, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_7 = QtGui.QLabel(self.centralwidget)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)
        self.label_9 = QtGui.QLabel(self.centralwidget)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 0, 0, 1, 1)
        self.label_10 = QtGui.QLabel(self.centralwidget)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 2, 0, 1, 1)
        self.gridLayout_7.addLayout(self.gridLayout, 3, 0, 1, 1)
        self.line_3 = QtGui.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout_7.addWidget(self.line_3, 2, 0, 1, 1)
        self.gridLayout_7.setColumnStretch(0, 1)
        self.gridLayout_7.setColumnStretch(1, 2)
        self.verticalLayout_4.addLayout(self.gridLayout_7)
        StillPublishUI.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(StillPublishUI)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 806, 21))
        self.menubar.setObjectName("menubar")
        StillPublishUI.setMenuBar(self.menubar)

        self.retranslateUi(StillPublishUI)
        QtCore.QMetaObject.connectSlotsByName(StillPublishUI)

    def retranslateUi(self, StillPublishUI):
        StillPublishUI.setWindowTitle(QtGui.QApplication.translate("StillPublishUI", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("StillPublishUI", "Source : ", None, QtGui.QApplication.UnicodeUTF8))
        self.logo_label.setText(QtGui.QApplication.translate("StillPublishUI", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.publish_pushButton.setText(QtGui.QApplication.translate("StillPublishUI", "Publish", None, QtGui.QApplication.UnicodeUTF8))
        self.design_radioButton.setText(QtGui.QApplication.translate("StillPublishUI", "Design", None, QtGui.QApplication.UnicodeUTF8))
        self.asset_radioButton.setText(QtGui.QApplication.translate("StillPublishUI", "Asset", None, QtGui.QApplication.UnicodeUTF8))
        self.scene_radioButton.setText(QtGui.QApplication.translate("StillPublishUI", "Scene", None, QtGui.QApplication.UnicodeUTF8))
        self.preview_label.setText(QtGui.QApplication.translate("StillPublishUI", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.status_label.setText(QtGui.QApplication.translate("StillPublishUI", "----", None, QtGui.QApplication.UnicodeUTF8))
        self.mode_label.setText(QtGui.QApplication.translate("StillPublishUI", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("StillPublishUI", "Department : ", None, QtGui.QApplication.UnicodeUTF8))
        self.entitySub1_label.setText(QtGui.QApplication.translate("StillPublishUI", "Type", None, QtGui.QApplication.UnicodeUTF8))
        self.entitySub2_label.setText(QtGui.QApplication.translate("StillPublishUI", "SubType", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("StillPublishUI", "Project", None, QtGui.QApplication.UnicodeUTF8))
        self.entity_label.setText(QtGui.QApplication.translate("StillPublishUI", "Asset", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("StillPublishUI", "Status", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("StillPublishUI", "Task", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("StillPublishUI", "User", None, QtGui.QApplication.UnicodeUTF8))

