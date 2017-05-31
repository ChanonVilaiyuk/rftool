import sys, os, subprocess
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

try: 
    import maya.cmds as mc 
    import maya.mel as mm
    isMaya=True
except ImportError: 
    isMaya = False

from startup import config
from startup import template
from rftool.utils import path_info
from rftool.utils import file_utils

if isMaya: 
    version = mc.about(v = True)
    if '2015' in version : 
        MAYA_PYTHON = 'C:/Program Files/Autodesk/Maya2015/bin/mayapy.exe'

    if '2016' in version : 
        MAYA_PYTHON = 'C:/Program Files/Autodesk/Maya2016/bin/mayapy.exe'
        MAYA_RENDER = 'C:/Program Files/Autodesk/Maya2016/bin/Render.exe'

    if '2017' in version : 
        MAYA_PYTHON = 'C:/Program Files/Autodesk/Maya2017/bin/mayapy.exe'


def create_asset_template(root, project, assetType, assetSubType, assetName):
    scriptServer = os.environ['RFSCRIPT']
    templatePath = ''
    rootValid = False

    if root == config.RFPROJECT:
        steps = template.workAssetSteps
        templatePath = '%s/RFPROJECT' % template.templatePath
        rootValid = True

    if root == config.RFPUBL:
        steps = template.publAssetSteps
        templatePath = '%s/RFPUBL' % template.templatePath
        rootValid = True

    if root == config.RFPROD:
        steps = template.prodAssetSteps
        templatePath = '%s/RFPROD' % template.templatePath
        rootValid = True

    if rootValid:
        asset = path_info.PathInfo(project=project, entity=config.asset, entitySub1=assetType, entitySub2=assetSubType, name=assetName)
        assetPath = asset.entityPath(root)

        if not os.path.exists(assetPath):
            os.makedirs(assetPath)

        for step in steps:
            src = '%s/%s' % (templatePath, step)
            dst = '%s/%s' % (assetPath, step)
            result = file_utils.copyTree(src, dst)
            logger.debug('Copy %s -> %s success' % (src, dst))

        create_standin(asset)
        repath_ad(asset)

        return True

def create_scene_template(root, project, episodeName, sequenceName, shotName):
    scriptServer = os.environ['RFSCRIPT']
    templatePath = ''
    rootValid = False

    if root == config.RFPROJECT:
        steps = template.workSceneSteps
        templatePath = '%s/RFPROJECT' % template.templatePath
        rootValid = True

    if root == config.RFPUBL:
        steps = template.publSceneSteps
        templatePath = '%s/RFPUBL' % template.templatePath
        rootValid = True

    if root == config.RFPROD:
        steps = template.prodSceneSteps
        templatePath = '%s/RFPROD' % template.templatePath
        rootValid = True

    if rootValid:
        shot = path_info.PathInfo(project=project, entity=config.scene, entitySub1=episodeName, entitySub2=sequenceName, name=shotName)
        shotPath = shot.entityPath(root)

        if not os.path.exists(shotPath):
            os.makedirs(shotPath)

        for step in steps:
            src = '%s/%s' % (templatePath, step)
            dst = '%s/%s' % (shotPath, step)

            if not os.path.exists(dst): 
                result = file_utils.copyTree(src, dst)
                logger.debug('Copy %s -> %s success' % (src, dst))

        return True


def create_standin(asset):
    assetPath = asset.entityPath('RFPROJECT')
    refPath = '%s/%s' % (assetPath, config.ref)
    files = file_utils.listFile(refPath)
    count = 0

    if files:
        for ref in files:
            if config.libFileReplaceKw in ref:
                newName = ref.replace(config.libFileReplaceKw, asset.name)
                src = '%s/%s' % (refPath, ref)
                dst = '%s/%s' % (refPath, newName)
                os.rename(src, dst)
                logger.debug('Renaming %s -> %s' % (src, dst))
                count+=1

    logger.info('renaming %s files standin complete (%s)' % (count, refPath))


def repath_ad(asset):
    assetPath = asset.entityPath('RFPROJECT')
    refPath = '%s/%s' % (assetPath, config.ref)
    files = file_utils.listFile(refPath)
    adFile = asset.libName('', 'ad', project=False)
    replaceDict = {config.assemblyMap['assetName']: '%s_ad' % asset.name, config.assemblyMap['locatorLabel']: asset.name}

    if os.path.exists('%s/%s' % (refPath, adFile)):

        if files:
            for k, v in config.representationMap.iteritems():
                replaceFile = [a for a in files if k in a]

                if replaceFile:
                    path = '%s/%s' % (refPath, replaceFile[0])
                    replaceDict.update({v: path})

            logger.debug('replaceKey %s' % str(replaceDict))
            logger.info('repath ad complete %s' % ('%s/%s' % (refPath, adFile)))
            return file_utils.search_replace_keys('%s/%s' % (refPath, adFile), replaceDict, backupFile=False)


def check_export(mtime, path):
    """ check if file export success by checking time stamp """
    if not os.path.exists(path):
        return False

    else:
        newtime = os.path.getmtime(path)

        if not newtime == mtime:
            return True
        else:
            return False

def check_time(path):
    if not os.path.exists(path):
        return 0
    else:
        return os.path.getmtime(path)


# def runMayaPy(runpy, *args) : 
#   """ run maya py subprocess """ 
#   logger.info('starting subprocess, please wait ...')
#   startupinfo = subprocess.STARTUPINFO()
    
#   # hide console 
#   # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
#   p = subprocess.Popen([MAYA_PYTHON, runpy] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
#   stdout, stderr = p.communicate()

#   logger.info(stdout)
#   logger.info(stderr)

#   logger.info('subprocess complete')


def runMayaPy(runpy, mayaVersion, console=True, *args) : 
    """ run maya py subprocess """ 
    logger.info('starting subprocess, please wait ...')

    if '2015' in mayaVersion : 
        MAYA_PYTHON = 'C:/Program Files/Autodesk/Maya2015/bin/mayapy.exe'

    if '2016' in mayaVersion : 
        MAYA_PYTHON = 'C:/Program Files/Autodesk/Maya2016/bin/mayapy.exe'
        MAYA_RENDER = 'C:/Program Files/Autodesk/Maya2016/bin/Render.exe'

    if '2017' in mayaVersion : 
        MAYA_PYTHON = 'C:/Program Files/Autodesk/Maya2017/bin/mayapy.exe'

    startupinfo = subprocess.STARTUPINFO()
    
    # hide console 
    if not console: 
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    p = subprocess.Popen([MAYA_PYTHON, runpy] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
    p.wait()
    stdout, stderr = p.communicate()

    logger.info(stdout)
    logger.info(stderr)

    logger.info('subprocess complete')

def search_replace_file(srcFile, dstFile, replaceDict) : 
    """ search and replace list of strings """ 
    # replaceDict = {'search': 'replace'}

    # open file 
    f = open(srcFile, 'r')
    data = f.read()
    f.close()

    for search, replace in replaceDict.iteritems(): 
        data = data.replace(search, replace)

    # write back 
    f = open(dstFile, 'w')
    f.write(data)
    f.close()

    return True