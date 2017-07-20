# System modules
import sys
import os
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Maya modules
# import maya.standalone
# maya.standalone.initialize(name='python')
import maya.cmds as mc
import maya.mel as mm
import pymel.core as pm

# from pymel.internal.startup import fixMayapy2011SegFault
# fixMayapy2011SegFault()


# assembly modules
# packagePath = '%s/python/2.7/site-packages' % os.environ['RFSCRIPT']
# toolPath = '%s/core/maya' % os.environ['RFSCRIPT']
# corePath = '%s/core' % os.environ['RFSCRIPT']
# qtPath = '%s/lib/Qt.py' % os.environ['RFSCRIPT']
# appendPaths = [packagePath, toolPath, corePath, qtPath]

# # add PySide lib path
# for path in appendPaths:
#     if not path in sys.path:
#         sys.path.append(path)

# from rftool.layout.split_shot import split_shot_cmd


# def run():
#     print 'aaaaaaaaaaaaaaaaaaaaaaaaa'
#     shotPath = sys.argv[1]

#     logger.debug('input argv')
#     logger.debug('shotPath %s' % shotPath)
#     # split_shot_cmd.split_shots(scenePath=shotPath)
#     logger.info('\nbatch complete\n')

# run()
# maya.standalone.uninitialize()
