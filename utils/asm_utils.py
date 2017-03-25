# sceneAssembly command utils
# create at 2015-12-09
# Written by ta.animator@gmail.com
# Modify at your own risk

# code start
# ==================================================================


# maya module
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMaya as om

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

version = mc.about(v = True)

if '2015' in version :
    if not mc.pluginInfo('sceneAssembly.mll', q=True, l=True) :
        mc.loadPlugin('C:\\Program Files\\Autodesk\\Maya2015\\bin\\plug-ins\\sceneAssembly.mll', qt = True)
        logger.debug('loadPlugin sceneAssembly success.')

    if not mc.pluginInfo('gpuCache.mll', q=True, l=True) :
        mc.loadPlugin("C:\\Program Files\\Autodesk\\Maya2015\\bin\\plug-ins\\gpuCache.mll", qt = True)
        logger.debug('loadPlugin gpuCache success.')

if '2016' in version :
    if not mc.pluginInfo('sceneAssembly.mll', q=True, l=True) :
        mc.loadPlugin('C:\\Program Files\\Autodesk\\Maya2016\\bin\\plug-ins\\sceneAssembly.mll', qt = True)
        logger.debug('loadPlugin sceneAssembly success.')

    if not mc.pluginInfo('gpuCache.mll', q=True, l=True) :
        mc.loadPlugin("C:\\Program Files\\Autodesk\\Maya2016\\bin\\plug-ins\\gpuCache.mll", qt = True)
        logger.debug('loadPlugin gpuCache success.')


''' create assembly definition node '''
def createADNode(name = 'assemblyDefinition') :
    node = mc.assembly(type = 'assemblyDefinition', name = name)
    return node

''' create assembly reference node '''
def createARNode(name = 'assemblyReference'):
    node = mc.assembly(type='assemblyReference', name = name)
    return node

''' set assembly reference definition path '''
def setARDefinitionPath(assemblyNode, path) :
    mc.setAttr('%s.definition' % assemblyNode, path, type = 'string')

def setARNamespace(assemblyNode, namespace) :
    mc.setAttr('%s.repNamespace' % assemblyNode, namespace, type = 'string')


''' add representations --> type = Scene / Cache / Locator '''
def addRepresentation(assemblyNode, type, path) :
    result = mc.assembly(assemblyNode, edit = True, createRepresentation = type, input = path)
    return result


''' add representations & rename & relabel --> type = Scene / Cache / Locator '''
def addRepresentation2(assemblyNode, type, path, newName, oldName):
    addRepresentation(assemblyNode, type, path)
    listNameIndex = listRepIndex(assemblyNode, listType = 'name')
    listLabelIndex = listRepIndex(assemblyNode, listType = 'label')

    # check if given name is in the representation list
    if oldName in listNameIndex :
        setName(assemblyNode, listNameIndex.index(oldName), newName)
        setLabel(assemblyNode, listNameIndex.index(oldName), newName)

        return True

    else :
        mm.eval('warning "No name [%s] in representation list";' % oldName)
        return False


''' set active representations '''
def setActiveRep(assemblyNode, name) :
    mc.assembly(assemblyNode, e = True, active = name)


''' query active representations '''
def getActiveRep(assemblyNode) :
    activeNode = mc.assembly(assemblyNode, q = True, active = True)

    return activeNode

def setAllActiveRep(assemblyNode) :
    """ switch representation to AR or Gpu """
    # switch to AR or Gpu
    targetName = ['AR', 'Gpu']
    current = getActiveRep(assemblyNode)

    # if current AR not AR or Gpu
    if not current in targetName :
        lists = listRepIndex(assemblyNode, listType = 'name')
        print assemblyNode

        if lists:
            if 'AR' in lists :
                setActiveRep(assemblyNode, 'AR')

            elif 'Gpu' in lists :
                setActiveRep(assemblyNode, 'Gpu')

    # find childs and check again
    ads = mc.listRelatives(assemblyNode, c = True, f = True)
    if ads:

        for ad in ads :
            if mc.objectType(ad, isType = 'assemblyReference') :
                setAllActiveRep(ad)


''' change label name by giving index item '''
def setLabel(assemblyNode, index, newName) :
    mc.setAttr('%s.representations[%s].repLabel' % (assemblyNode, index), newName, type = 'string')


''' change name by giving index item '''
def setName(assemblyNode, index, newName) :
    activeNode = getActiveRep(assemblyNode)

    mc.setAttr('%s.representations[%s].repName' % (assemblyNode, index), newName, type = 'string')


''' query representation lists --> listType = name / label '''
def listRepIndex(assemblyNode, listType = 'name') :
    lists = mc.assembly(assemblyNode, q = True, listRepresentations = True)

    if listType == 'name' :
        return lists

    labels = []
    datas = []

    if lists :
        for i in range(len(lists)) :
            label = mc.getAttr('%s.representations[%s].repLabel' % (assemblyNode, i))
            data = mc.getAttr('%s.representations[%s].repData' % (assemblyNode, i))
            labels.append(label)
            datas.append(data)

    if listType == 'label' :
        return labels

    if listType == 'data' :
        return datas


''' GPU '''
''' export GPU cache : option time = still/animation '''
def exportGPUCache(exportObjects, exportPath, abcName, time = 'still') :
    startFrame = 1.0
    endFrame = 1.0

    if time == 'still' :
        currentFrame = mc.currentTime(q = True)
        startFrame = currentFrame
        endFrame = currentFrame

    if time == 'animation' :
        startFrame = mc.playbackOptions(q = True, min = True)
        endFrame = mc.playbackOptions(q = True, max = True)

    # export objs
    validObjs = [a for a in exportObjects if mc.objExists(a)]
    objNotExists = [a for a in exportObjects if not mc.objExists(a)]

    if validObjs :
        mc.select(validObjs)
        result = mc.gpuCache(exportObjects,
                                startTime = startFrame,
                                endTime = endFrame,
                                optimize = True,
                                optimizationThreshold = 40000,
                                writeMaterials = True,
                                dataFormat = 'ogawa',
                                directory = exportPath,
                                fileName = abcName,
                                saveMultipleFiles = False
                                )

        gpupath = '%s/%s.abc' %(exportPath,abcName)

        if objNotExists :
            mm.eval('warning "%s not exists and will not be exported";' % objNotExists)

        return result

    else :
        mm.eval('warning "Objects not exists";' % objNotExists)
        return False


def exportGPUCacheGrp(exportGrp, exportPath, abcName, time = 'still') :
    startFrame = 1.0
    endFrame = 1.0

    if time == 'still' :
        currentFrame = mc.currentTime(q = True)
        startFrame = currentFrame
        endFrame = currentFrame

    if time == 'animation' :
        startFrame = mc.playbackOptions(q = True, min = True)
        endFrame = mc.playbackOptions(q = True, max = True)

    # export objs
    if mc.objExists(exportGrp) :
        mc.select(exportGrp)
        result = mc.gpuCache(exportGrp,
                                startTime = startFrame,
                                endTime = endFrame,
                                optimize = True,
                                optimizationThreshold = 40000,
                                writeMaterials = True,
                                dataFormat = 'ogawa',
                                directory = exportPath,
                                fileName = abcName,
                                saveMultipleFiles = False
                                )

        gpupath = '%s/%s.abc' % (exportPath,abcName)

        return result


def etc() :
    path = 'O:/pipeline/abcTest/asset/3D/prop/tree/pineA/ref'
    assetName = path.split('/')[-2]

    # create assemble definition
    mc.assembly(name= '%s_ad' %(assetName))
    # create assemble 'Locator' representation
    mc.assembly('%s_ad' %(assetName), edit=True, createRepresentation='Locator', repName='Loc', repLabel='Loc', input=assetName)

    for root, dirs, files in os.walk(path):
        allreps = root, dirs, files

    for f in files:
        name = f.split('_')[-1].split('.')[0]
        pathinput = '%s/%s' %(path,f)
        # create assembly 'Scene' representation
        if '.ma' in f:
            print name
            mc.assembly('%s_ad' %(assetName), edit=True, createRepresentation='Scene', repName=name, input=pathinput, repLabel=name)
        # create assembly 'Cache' representation
        if '.abc' in f:
            print name
            mc.assembly('%s_ad' %(assetName), edit=True, createRepresentation='Cache', repName=name, input=pathinput, repLabel=name)

def getAsmListEdit(assemblyNode):
    """ Get asm list edit by nunu """
    # get assembly node MObject
    mSel = om.MSelectionList()
    mSel.add(assemblyNode)
    mObj = om.MObject()
    mSel.getDependNode(0, mObj)

    # iterate thru each edit using MItEdits
    mItEdits = om.MItEdits(mObj)
    editStrs = []

    # store edit string in this list
    while not mItEdits.isDone():
        mEdit = mItEdits.edit()
        editStr = mEdit.getString()
        editStrs.append(editStr)
        mItEdits.next()

    return editStrs
