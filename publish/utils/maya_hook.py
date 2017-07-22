import sys
import os 
import maya.cmds as mc 
import maya.mel as mm

# maya commands 

def save_file(saveFile): 
    result = mc.file(save=True, type='mayaAscii')
    return result

def save_file_as(saveFile): 
    mc.file(rename=saveFile)
    result = mc.file(save=True, type='mayaAscii')
    return result

def open_file(path): 
    return mc.file(path, o=True, f=True)

def check_scene_modify(): 
    return mc.file(q=True, modified=True)

def get_user(): 
    localUser = mc.optionVar(q=config.localUser)
    return localUser
