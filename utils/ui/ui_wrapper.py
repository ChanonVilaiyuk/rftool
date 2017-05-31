# Import python modules
import sys, os, re

# Import GUI
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui


def insert_column(tableWidget, columnName, columnIndex) :
    """ add a column on table """
    tableWidget.insertColumn(columnIndex)
    item = QtWidgets.QTableWidgetItem()
    item.setText(columnName)
    tableWidget.setHorizontalHeaderItem(columnIndex, item)

def remove_column(tableWidget, columnIndex) :
    """ remove column on table """
    tableWidget.removeColumn(columnIndex)

def set_label_icon(labelWidget, text='', iconPath='', size=[16, 16]) :
    if os.path.exists(iconPath) :
        labelWidget.setPixmap(QtGui.QPixmap(iconPath).scaled(size[0], size[1], QtCore.Qt.KeepAspectRatio))

    elif text :
        labelWidget.setText(text)

def set_label(labelWidget, text='', iconPath='', textColor=[], bgColor=[], size=[16, 16]) :
    bgStr = str()
    textStr = str()
    if text :
        labelWidget.setText(text)
    if bgColor :
        bgStr = 'background-color: rgb(%s, %s, %s);' % (bgColor[0], bgColor[1], bgColor[2])
    if textColor :
        textStr = 'color: rgb(%s, %s, %s);' % (textColor[0], textColor[1], textColor[2])

    styleStr = ('\n').join([bgStr, textStr])

    labelWidget.setStyleSheet('''
                                QLabel {
                                %s
                                }''' % styleStr)


def clear_table(tableWidget) :
    """ clear all data in table """
    rows = tableWidget.rowCount()

    for each in range(rows) :
        tableWidget.removeRow(0)

def insert_row(tableWidget, row, height) :
    """ insert table row """
    tableWidget.insertRow(row)
    tableWidget.setRowHeight(row, height)

def fill_table(tableWidget, row, column, text, iconPath='', color=[1, 1, 1]) :
    """ fill data in table """
    item = QtWidgets.QTableWidgetItem()
    item.setText(text)

    if iconPath :
        icon = QtWidgets.QIcon()
        icon.addPixmap(QtWidgets.QPixmap(iconPath), QtWidgets.QIcon.Normal, QtWidgets.QIcon.Off)
        item.setIcon(icon)

    if color :
        item.setBackground(QtGui.QColor(color[0], color[1], color[2]))

    tableWidget.setItem(row, column, item)

def get_all_items_listWidget(listWidget) :
    """ get all widget items """

    count = listWidget.count()
    items = []

    for i in range(count) :
        item = listWidget.item(i)
        items.append(item)

    return items

def get_selected_item_listWidget(listWidget) :
    return listWidget.selectedItems()

def get_current_item_listWidget(listWidget) :
    return listWidget.currentItem()

def add_item_listWidget(listWidget, text, color=[], iconPath='', iconSize=32):
    item = QtGui.QListWidgetItem(listWidget)
    item.setText(text)

    if os.path.exists(iconPath):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconPath),QtGui.QIcon.Normal,QtGui.QIcon.Off)
        item.setIcon(icon)
        item.setData(QtCore.Qt.UserRole, iconPath)
        listWidget.setIconSize(QtCore.QSize(iconSize, iconSize))

    if color:
        item.setBackground(QtGui.QColor(color[0], color[1], color[2]))

def add_item_data_listWidget(listWidget, text, color=[], iconPath='', iconSize=32, data=None):
    item = QtGui.QListWidgetItem(listWidget)
    item.setText(text)

    if os.path.exists(iconPath):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconPath),QtGui.QIcon.Normal,QtGui.QIcon.Off)
        item.setIcon(icon)
        listWidget.setIconSize(QtCore.QSize(iconSize, iconSize))

    if data:
        item.setData(QtCore.Qt.UserRole, data)

    if color:
        item.setBackground(QtGui.QColor(color[0], color[1], color[2]))

def set_tableWidget_item(item, text, bgColor=[]):
    item.setText(text)

    if bgColor:
        item.setBackground(QtGui.QColor(bgColor[0], bgColor[1], bgColor[2]))

def get_tableWidget_item(tableWidget, row, column, widget=False):
    if widget:
        return tableWidget.cellWidget(row, column)
    return tableWidget.item(row, column)

def get_tableWidget_all_items(tableWidget, column, widget=False):
    rows = tableWidget.rowCount()
    items = []

    for row in range(rows):
        if not widget:
            items.append(tableWidget.item(row, column))
        else:
            items.append(tableWidget.cellWidget(row, column))
    return items

def match_table_row(tableWidget, column, data):
    items = get_tableWidget_all_items(tableWidget, column)
    strData = [str(a.text()) for a in items]
    print 'strData', strData
    print 'match', data

    if data in strData:
        return strData.index(data)

def set_icon_listWidget(listWidget, row, iconPath):
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(iconPath),QtGui.QIcon.Normal,QtGui.QIcon.Off)
    item = listWidget.item(row)
    item.setIcon(icon)

def add_text_listWidget(lineEdit, listWidget) :
    """ add link path to UI """
    # input from lineEdit
    strInput = str(lineEdit.text())
    # lineEdit.clear()

    iconPath = icon.ready

    if strInput :
        items = get_all_items_listWidget(listWidget)
        strItems = [str(a.text()) for a in items]

        if not strInput in strItems :
            add_item_listWidget(listWidget, strInput, iconPath=iconPath, iconSize=16)
            return True
        else :
            return False

def remove_text_listWidget(listWidget) :
        """ remove shot from UI """
        items = listWidget.selectedItems()

        for item in items :
            listWidget.takeItem(listWidget.row(item))

def set_button_label(button, text, iconPath=None, bgColor=None):
    button.setText(text)

    if iconPath:
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconPath),QtGui.QIcon.Normal,QtGui.QIcon.Off)
        button.setIcon(icon)

    if bgColor:
        color = 'background-color: rgb(%s, %s, %s)' % (bgColor[0], bgColor[1], bgColor[2])
        button.setStyleSheet(color)

def set_comboBox_color(comboBox, bgColor=None):
    color = 'background-color: rgb(%s, %s, %s)' % (bgColor[0], bgColor[1], bgColor[2])
    comboBox.setStyleSheet(color)

def set_lineEdit(lineEdit, text='', bgColor=None):
    if text:
        lineEdit.setText(str(text))

    if bgColor:
        color = 'background-color: rgb(%s, %s, %s)' % (bgColor[0], bgColor[1], bgColor[2])
        lineEdit.setStyleSheet(color)

    else:
        lineEdit.setStyleSheet('')
