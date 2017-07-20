import sys
import os 
import logging 
import maya.cmds as mc 

logger = logging.getLogger(__name__)
from startup import config
reload(config)

# precheck module 
def check_naming(): 
	""" Check for duplicated name """ 
	geoGrp = config.geoGrp
	if geoGrp : 
		try : 
			mc.select(geoGrp, hi = True)
			objs = mc.ls(sl = True, type = 'transform')
			dups = []

			for each in objs : 
				if '|' in each : 
					dups.append(each)

			mc.select(cl = True)

			if not dups : 
				return True, 'Success'

			else : 
				return False, 'Objects have duplicated name %s' % dups

		except Exception as e : 
			print e 
			return False, str(e)

def check_group(): 
	""" check Rig_Grp """ 
	checkGrp = config.rigGrp

	if mc.objExists(checkGrp): 
		return True, 'Success' 
	else: 
		return False, 'No Rig_Grp'
	
