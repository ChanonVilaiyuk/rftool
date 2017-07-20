import os
import sys 
from collections import OrderedDict
import yaml

#Import maya commands
try:
    import maya.cmds as mc
    import maya.mel as mm
    import maya.OpenMayaUI as mui

    isMaya = True
except ImportError:
    isMaya = False
    packagePath = '%s/python/2.7/site-packages' % os.environ['RFSCRIPT']
    toolPath = '%s/core/maya' % os.environ['RFSCRIPT']
    corePath = '%s/core' % os.environ['RFSCRIPT']
    qtPath = '%s/lib/Qt.py' % os.environ['RFSCRIPT']
    appendPaths = [packagePath, toolPath, corePath, qtPath]

    # add PySide lib path
    for path in appendPaths:
        if not path in sys.path:
            sys.path.append(path)

    from startup import setEnv
    reload(setEnv)
    setEnv.set()

from rftool.utils import path_info
reload(path_info)
from rftool.utils import file_utils
import logging 
logger = logging.getLogger(__name__)

# predefined variable 
assetName = 'assetName'
taskName = 'taskName'
workfile = 'workfile'
publishFile = 'publishFile'
incrementWorkFile = 'incrementWorkFile'
publishImgFiles = 'publishImgFiles'
publishMovFiles = 'publishMovFiles'
heroImgFile = 'heroImgFile'
heroMovFile = 'heroMovFile'
previewFile = 'previewFile'

class TaskInfo(object):
    """docstring for TaskInfo"""
    def __init__(self, entity):
        super(TaskInfo, self).__init__()
        self.entity = entity
        self.dataExt = 'yml'
        self.primaryKey = ['work', 'primaryOutput', 'secondaryOutput', 'shotgun', 'taskName']
        self.secondaryKey = ['workfile', 'incrementWorkFile', 'publishFile', 'publishImgFiles', 'publishMovFiles', 
                            'heroImgFile', 'heroMovFile', 'previewFile', 'abc', 'project_entity', 
                            'asset_entity', 'task_entity', 'task_status', 'version_entity', 
                            'version_status']



        self.templateDict = dict()
        self.set_template()

    def read(self): 
        path = self.path()
        data = ymlLoader(path) 
        return data

    def path(self): 
        dataPath = self.entity.publishPath(publish='data')
        dataFile = '{0}.{1}'.format(self.entity.basename(ext=False), self.dataExt)
        dataFilePath = '{0}/{1}'.format(dataPath, dataFile)

        if not os.path.exists(dataPath): 
            os.makedirs(dataPath)
            logger.debug('create %s' % dataPath)

        if not os.path.exists(dataFilePath): 
            ymlDumper(dataFilePath, self.templateDict)
            logger.debug('create file %s' % dataFilePath)

        return dataFilePath

    def write(self, data): 
        dataFile = self.path()
        ymlDumper(dataFile, data)


    def append(self, data): 
        currentData = self.read()
        currentData.update(data)
        self.write(currentData)
        logger.debug('data append %s' % data)

    def set(self, key1, key2, value): 
        tempDict = dict()
        if key1 in self.primaryKey: 
            if key2 in self.secondaryKey: 
                data = self.read()
                tempDict.update({key1: {key2: value}})
                
                if not key1 in data.keys(): 
                    data.update(tempDict)
                else: 
                    data[key1].update({key2: value})

                self.append(data)
                logger.info('data set %s' % tempDict)

            else: 
                logger.warning('invalid key %s' % (key2))  
        else: 
            logger.warning('invalid key %s' % (key1))

    def get(self, key1, key2): 
        if key1 in self.primaryKey: 
            if key2: 
                if key2 in self.secondaryKey: 
                    data = self.read()
                    value = data.get(key1).get(key2)
                    return value 

                else: 
                    logger.warning('invalid key %s' % (key2))  
            else: 
                data = self.read()
                value = data.get(key1)
                return value

        else: 
            logger.warning('invalid key %s' % (key1))


    def set_template(self): 
        self.templateDict['project'] = self.entity.project
        self.templateDict['assetName'] = self.entity.name
        self.templateDict['department'] = self.entity.step 
        self.templateDict['taskName'] = self.entity.taskName

        self.templateDict['work'] = dict()
        self.templateDict['primaryOutput'] = dict()
        self.templateDict['secondaryOutput'] = dict()
        self.templateDict['shotgun'] = dict()


class AssetInfo(object):
    """docstring for AssetInfo"""
    def __init__(self, entity):
        super(AssetInfo, self).__init__()
        self.entity = entity
        self.dataExt = 'yml'

        self.templateDict = dict()
        self.set_template()

    def write(self): 
        dataFilePath = self.entity.dataFile()
        dataPath = os.path.dirname(dataFilePath)

        if not os.path.exists(dataPath): 
            os.makedirs(dataPath)
            logger.debug('create %s' % dataPath)

        if not os.path.exists(dataFilePath): 
            ymlDumper(dataFilePath, self.templateDict)
            logger.debug('create file %s' % dataFilePath)

        return dataFilePath

    def read(self): 
        dataFilePath = self.entity.dataFile() 

        if not os.path.exists(dataFilePath): 
            self.write()
        data = ymlLoader(dataFilePath) 
        return data

    def setData(self, data): 
        self.fileData = self.read()
        self.fileData.update(data)
        return self.fileData

    def publish(self): 
        data = self.fileData
        dataFilePath = self.entity.dataFile()
        ymlDumper(dataFilePath, data)

        version = self.incrementFile()
        return file_utils.copy(dataFilePath, version)


    def incrementFile(self): 
        dataPath = self.entity.dataPath()
        version = file_utils.find_next_version(file_utils.listFile(dataPath))
        versionData = self.entity.dataFile(version)

        return versionData

    def set_template(self): 
        self.templateDict['project'] = self.entity.project 
        self.templateDict['asset'] = self.entity.name
        self.templateDict['assetType'] = self.entity.type
        self.templateDict['assetSubType'] = self.entity.subtype
        self.templateDict['assetID'] = 0
        self.templateDict['assetType'] = self.entity.type
        self.templateDict['assetType'] = self.entity.type


def ymlDumper(file, dictData) :
    # input dictionary data
    data = yaml.dump(dictData, default_flow_style=False)
    result = writeFile(file, data)

    return result

def ymlLoader(file) :
    data = readFile(file)
    dictData = yaml.load(data)

    return dictData
        
def writeFile(file, data) :
    f = open(file, 'w')
    f.write(data)
    f.close()
    return True


def readFile(file) :
    f = open(file, 'r')
    data = f.read()
    return data

