import os
import sys 
import logging 
logger = logging.getLogger(__name__)

import maya.cmds as mc 
from rftool.utils import maya_utils
from rftool.utils import abc_utils
from rftool.publish.utils import pub_utils
from startup import config
reload(maya_utils)
reload(config)
reload(pub_utils)
reload(abc_utils)

# publish for model 
ui = None
def export_abc(entity=None): 
	""" export alembic geo """ 
	status = False 
	exportGrp = config.geoGrp
	res = entity.task_res()
	libPath = entity.libPath()

	if res: 
		abcModel = entity.libName(entity.step, res, ext='abc')
		exportPath = '{0}/{1}'.format(libPath, abcModel)

		# check file 
		start = pub_utils.file_time(exportPath)

		# export command 
		abc_utils.exportABC(exportGrp, exportPath)

		# check file export success 
		end = pub_utils.file_time(exportPath)
		success = pub_utils.is_file_new(start, end)

		if success: 
			return True, 'Success %s' % exportPath

		else: 
			return False, 'Failed to export Alembic %s' % exportPath

	else: 
		return False, 'No res found'

def export_gpu(entity=None): 
	""" export GPU for AD """ 
	status = False 
	exportGrp = config.geoGrp
	res = entity.task_res()
	libPath = entity.libPath()

	if res: 
		abcName = entity.libName(config.libName.get('gpu'), res, ext='abc')

		# name without ext 
		basename = os.path.splitext(abcName)[0]
		
		gpuName = '{0}/{1}'.format(libPath, abcName)

		start = pub_utils.file_time(gpuName)

		# export GPU command 
		result = maya_utils.exportGPUCacheGrp(exportGrp, libPath, basename, time='still')
		
		end = pub_utils.file_time(gpuName)
		success = pub_utils.is_file_new(start, end)

		if success: 
			return True, 'Success %s' % gpuName

		else: 
			return False, 'Failed to export Gpu %s' % gpuName

	else: 
		return False, 'No res found'

