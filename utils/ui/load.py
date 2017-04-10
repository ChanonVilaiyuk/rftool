import os
import sys
from Qt import QtCore
from Qt import QtWidgets
from Qt import _QtUiTools

def loadUI(uiFile, parent): 
    """ Qt Module to load .ui file """ 
    # read .ui directly
    moduleDir = os.path.dirname(uiFile)
    loader = _QtUiTools.QUiLoader()
    loader.setWorkingDirectory(moduleDir)

    f = QtCore.QFile(uiFile)
    f.open(QtCore.QFile.ReadOnly)

    myWidget = loader.load(f, parent)
    f.close()

    return myWidget