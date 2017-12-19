# run when scene is open 
import sys
import os 
import maya.cmds as mc 
import maya.mel as mm 
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from rftool.utils import maya_utils

def scene_open(): 
	logger.info('On scene_open script running ...')
	logger.info('Cleaning plugin ...')
	maya_utils.remove_plugins()