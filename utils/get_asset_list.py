# System modules
import sys
import os
import re
import shutil
import logging

# Maya modules
import maya.standalone
import maya.cmds as mc
import maya.mel as mm

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def main() :
	mayaFile = sys.argv[1]
	maya.standalone.initialize( name='python' )
	
	mc.file(mayaFile, force=True , open=True, loadReferenceDepth = "all")
	logger.info('open %s' % mayaFile)

	files = mc.file(query=1, list=1, withoutCopyNumber=1)
	logger.info('find all refs %s' % files)

	assemblyFiles = ''
	# assemblyFiles = getAssemblyFiles()
	textureFiles = getTextureFile()
	tmpFile = 'mayaAssetList.txt'
	tmpdir = os.getenv('TMPDIR')
	tmpPath = '%s/%s' % (tmpdir, tmpFile)

	data = {'files': files, 'assemblyFiles': assemblyFiles, 'textureFiles': textureFiles}

	f = open(tmpPath, 'w')
	f.write(str(data))
	f.close()
	logger.info('write data complete')


def getTextureFile() : 
    fileNodes = mc.ls(type = 'file')
    files = []

    if fileNodes : 
        for each in fileNodes : 
            fileTexture = mc.getAttr('%s.fileTextureName' % each)

            fileStatus = False 
            if os.path.exists(fileTexture) : 
                fileStatus = True 

            files.append((fileTexture, fileStatus))

    return files


def getAssemblyFiles() : 
    sels = mc.ls(type = 'assemblyReference')
    copyFiles = []

    if sels : 
        for each in sels : 
            ad = mc.getAttr('%s.definition' % each)
            
            if ad : 
                fileStatus = False

                if os.path.exists(ad) : 
                    fileStatus = True
                    
                copyFiles.append((ad, fileStatus))

            datas = listRepIndex(each, 'data')
            
            if datas : 
                for each in datas : 
                    fileStatus = False
                    if os.path.exists(each) : 
                        fileStatus = True
                        
                    copyFiles.append((each, fileStatus))

    return copyFiles


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

main()
