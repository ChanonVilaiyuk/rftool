import os
import sys
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

import maya.cmds as mc 
import maya.mel as mm 

def saveSplitFile(shot): 
    initVersion = 'v001'
    shotPath = shot.entityPath()
    shotFileName = '%s_%s_split.ma' % (shot.shotName(project=True, step=True), initVersion)
    workPath = shot.workspacePath()
    outputPath = '%s/%s' % (workPath, shotFileName)
    logger.debug('outputPath %s' % outputPath)

    if not os.path.exists(workPath): 
        os.makedirs(workPath)
        logger.debug('make dir %s' % workPath)

    mc.file(rename=outputPath)
    result = mc.file(save=True, type='mayaAscii')
    logger.info(result)
    return result 


def saveTmpFile(shot): 
    dirname = os.path.dirname(shot.path)
    tmpName = '%s_tmp.ma' % shot.basename(ext=False)
    tmpFile = '%s/%s' % (dirname, tmpName)

    mc.file(rename=tmpFile)
    result = mc.file(save=True, type='mayaAscii')
    logger.info('Create tmp file success %s' % result)