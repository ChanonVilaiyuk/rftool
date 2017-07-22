# standard publish 
import os
import sys
import logging
logger = logging.getLogger(__name__)

from rftool.utils import path_info 
from rftool.utils import file_utils 
from rftool.publish.utils import maya_hook as hook
from rftool.publish.utils import pub_utils
from rftool.publish.utils import publish_info
from startup import config
reload(hook)
reload(pub_utils)
reload(publish_info)
ui = None

# precheck module 
def summarized_info(*args): 
	""" write published info from Task to Asset info """ 
	# get publish info 
	if ui: 
		publishFile = str(ui.publishVersionLabel.text())
		pubEntity = path_info.PathInfo(publishFile)
		taskInfo = publish_info.TaskInfo(pubEntity)
		assetInfo = publish_info.AssetInfo(pubEntity)

		data = assetInfo.read()
		taskDict = dict()

		# set 
		# asset id 
		assetEntity = taskInfo.get('shotgun', 'asset_entity')
		data.update({'assetID': assetEntity.get('id')})

		# task id 
		taskEntity = taskInfo.get('shotgun', 'task_entity')

		# publish file 
		output = taskInfo.get('primaryOutput', 'publishFile')
		# hero file 
		outputHero = taskInfo.get('primaryOutput', 'heroFile')

		# user 
		versionEntity = taskInfo.get('shotgun', 'version_entity')
		user = str()
		if versionEntity: 
			user = versionEntity.get('user', {}).get('name')

		# set dict
		taskDict = {pubEntity.taskName: {'id': taskEntity.get('id'), 'output': output, 'user': user}, 'output': output, 'outputHero': outputHero, 'user': user}

		# set department
		if pubEntity.step in data.keys(): 
			data[pubEntity.step].update(taskDict)

		else:
			data.update({pubEntity.step: taskDict})

		assetInfo.setData(data)
		result = assetInfo.publish()

		return True, 'Success \npublish info %s' % result

	else: 
		logger.warning('No ui information')
		return False, 'No ui information'

