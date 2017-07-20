# standard publish 
import os
import sys
import logging
logger = logging.getLogger(__name__)

from rftool.utils import sg_process
from rftool.utils import path_info
from rftool.publish.utils import publish_info
reload(sg_process)


ui = None

def publish_version(entity=None, publishFile=None): 
	""" create version in shotgun """ 
	userEntity = None
	message = str()
	processStatus = False

	# get publish info 
	if not publishFile: 
		if ui: 
			publishFile = str(ui.publishVersionLabel.text())
			userEntity = ui.userWidget.read()

	if publishFile: 
		pubEntity = path_info.PathInfo(publishFile)
		info = publish_info.TaskInfo(pubEntity)
		taskName = info.get('taskName', '')

		# create_version
		project = entity.project 
		assetName = entity.name

		# find key data 
		assetEntity = sg_process.get_one_asset(project, assetName)
		info.set('shotgun', 'asset_entity', assetEntity)

		projectEntity = assetEntity.get('project', None)
		info.set('shotgun', 'project_entity', projectEntity)

		taskEntity = sg_process.get_one_task(assetEntity, taskName)
		info.set('shotgun', 'task_entity', taskEntity)

		# if key data found 
		if assetEntity and projectEntity and taskEntity: 
			versionName = pubEntity.basename(ext=False)
			status = ui.statusWidget.get_task_status()
			description = ''
			playlistEntity = None
			result = sg_process.publish_version(projectEntity, assetEntity, taskEntity, userEntity, versionName, status, description, playlistEntity)

			message = 'Version creation not success'
			if result: 
				info.set('shotgun', 'version_entity', result)
				processStatus = True
				message = 'Success %s' % result

		else: 
			message = 'Data missing %s %s %s' % (assetEntity, projectEntity, taskEntity)
			logger.warning(message)
			processStatus = False

	else: 
		message = 'No Publish File input'
		logger.warning(message)
		processStatus = False

	return processStatus, message

def set_task(entity=None, publishFile=None): 
	""" change task status """
	message = str()
	processStatus = False

	# get publish info 
	if not publishFile: 
		if ui: 
			publishFile = str(ui.publishVersionLabel.text())

	if publishFile: 
		pubEntity = path_info.PathInfo(publishFile)
		info = publish_info.TaskInfo(pubEntity)
		taskEntity = info.get('shotgun', 'task_entity')
		taskName = info.get('taskName', '')

		# if no data in publish_info, query from shotgun
		if not taskEntity: 
			logger.debug('taskEntity not found in publish_info')
			project = pubEntity.project 
			assetName = pubEntity.name
			assetEntity = sg_process.get_one_asset(project, assetName)
			info.set('shotgun', 'asset_entity', assetEntity)
			
			taskEntity = sg_process.get_one_task(assetEntity, taskName)
			info.set('shotgun', 'task_entity', taskEntity)

		if taskEntity: 
			status = ui.statusWidget.get_task_status()
			data = {'sg_status_list': status}
			result = sg_process.set_task_data(taskEntity.get('id'), data)
			processStatus = True 
			message = 'Success %s' % result 

		else: 
			message = 'Failed to get taskEntity'

	return processStatus, message

def upload_thumbnail(entity=None, publishFile=None): 
	""" upload thumbnail to version """ 
	message = str()
	processStatus = False

	# get publish info 
	if not publishFile: 
		if ui: 
			publishFile = str(ui.publishVersionLabel.text())

	if publishFile: 
		pubEntity = path_info.PathInfo(publishFile)
		info = publish_info.TaskInfo(pubEntity)
		heroImgFile = info.get('primaryOutput', 'heroImgFile')
		versionEntity = info.get('shotgun', 'version_entity')
		
		if os.path.exists(heroImgFile) and versionEntity: 
			uploadFile = heroImgFile.replace('/', '\\')
			result = sg_process.update_entity_thumbnail('Version', versionEntity.get('id'), uploadFile)

			if result: 
				message = 'Success %s' % result
				processStatus = True

			else: 
				message = 'Failed to upload thumbnail'
				logger.warning(message)

		else: 
			message = 'Path %s not exists or versionEntity %s not found' % (heroImgFile, versionEntity)
			logger.warning(message)

	return processStatus, message


def upload_media(entity=None, publishFile=None): 
	""" upload mov file to version """ 
	message = str()
	processStatus = False

	# get publish info 
	if not publishFile: 
		if ui: 
			publishFile = str(ui.publishVersionLabel.text())

	if publishFile: 
		pubEntity = path_info.PathInfo(publishFile)
		info = publish_info.TaskInfo(pubEntity)
		heroMovFile = info.get('primaryOutput', 'heroMovFile')
		versionEntity = info.get('shotgun', 'version_entity')
		
		if os.path.exists(heroMovFile) and versionEntity: 
			uploadFile = heroMovFile.replace('/', '\\')
			result = sg_process.upload_version_media(versionEntity, uploadFile)

			if result: 
				message = 'Success %s' % result
				processStatus = True

			else: 
				message = 'Failed to upload movie'
				logger.warning(message)

		else: 
			message = 'Path %s not exists or versionEntity %s not found' % (heroImgFile, versionEntity)
			logger.warning(message)

	return processStatus, message
	
