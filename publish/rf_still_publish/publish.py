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
reload(hook)
reload(pub_utils)
reload(publish_info)
ui = None

def publish_file(entity=None): 
	""" publish work file """
	errorMessage = []
	
	if not entity: 
		entity = path_info.PathInfo()

	if entity: 
		logger.debug('start publishing ...')

		# get publish info 
		publishFile, saveWorkFile, incrementSaveWorkFile, libFile = pub_utils.get_publish_info(entity)
		
		logger.debug('save work file %s' % saveWorkFile)
		logger.debug('publish version %s' %  publishFile)
		logger.debug('save increment work file %s' % incrementSaveWorkFile)

		# start process files 
		saveResult = None
		publishResult = None
		workResult = None

		# publish info 
		pubEntity = path_info.PathInfo(publishFile)
		info = publish_info.TaskInfo(pubEntity)

		# save as
		saveResult = hook.save_file_as(incrementSaveWorkFile)
		info.set('work', 'incrementWorkFile', incrementSaveWorkFile)

		if saveResult: 
			# copy to publish 
			publishResult = file_utils.copy(saveResult, publishFile)
			info.set('primaryOutput', 'publishFile', publishFile)
			
			# copy to hero 
			# disable. Not all department export to lib, move to dept publish
			# publishHeroResult = file_utils.copy(saveResult, libFile)
			# info.set('primaryOutput', 'heroFile', libFile)

			# copy to current work version (short cut for overwritten save)
			workResult = file_utils.copy(saveResult, saveWorkFile)
			info.set('work', 'workfile', saveWorkFile)


		if not saveResult: 
			logger.error('Save to %s has failed' % incrementSaveWorkFile)
			errorMessage.append('Save to %s has failed' % incrementSaveWorkFile)

		if not publishResult: 
			logger.error('Publish to %s has failed' % publishFile)
			errorMessage.append('Publish to %s has failed' % publishFile)

		# if not publishHeroResult: 
		# 	logger.error('Publish to hero %s has failed' % libFile)
		# 	errorMessage.append('Publish to %s has failed' % libFile)

		if not workResult: 
			logger.error('Overwrite work version %s has failed' % saveWorkFile)
			errorMessage.append('Overwrite work version %s has failed' % saveWorkFile)

	if errorMessage: 
		return False, errorMessage

	else: 
		return True, 'Success \n%s' % publishResult
	

def publish_image(entity=None): 
	""" publish image or movie files """
	mediaExts = ['.mov']
	errorMessage = []
	imgPublishes = []
	if not entity: 
		entity = path_info.PathInfo()

	if entity and ui: 
		logger.debug('start publishing image ...')
		
		# get publish info 
		publishFile = str(ui.publishVersionLabel.text())
		pubEntity = path_info.PathInfo(publishFile)
		info = publish_info.TaskInfo(pubEntity)
		# successPublishFile = info.get('primaryOutput', 'publishFile')
		successPublishFile = publishFile

		# if publish success 
		if successPublishFile: 
			publishVer = path_info.find_version(successPublishFile)

			# _media path for hero preview 
			mediaPath = entity.mediaPath()
			publishImgPath = entity.publishPath(publish='img')
			publishMovPath = entity.publishPath(publish='mov')

			publishName = entity.publishName()
			publishMediaVersion = entity.publishName(publishVer)

			# get publish items 
			paths = ui.snapWidget.get_all_paths()
			heroImgSrc = None
			heroMovSrc = None
			copyDict = dict()

			for i, path in enumerate(paths): 
				src = path.replace('\\', '/')
				extension = os.path.splitext(path)[-1]
				basename = '%s_%03d%s' % (publishMediaVersion, i+1, extension)

				if extension in mediaExts: 
					dst = '{0}/{1}'.format(publishMovPath, basename)
					if not heroMovSrc: 
						heroMovSrc = src 
				else: 
					dst = '{0}/{1}'.format(publishImgPath, basename)
					if not heroImgSrc: 
						heroImgSrc = src
					
				copyDict.update({src: dst})

			# copy to publishes
			for src, dst in copyDict.iteritems(): 
				try: 
					file_utils.copy(src, dst)
					logger.debug('Copy to publish %s - %s' % (src, dst))
					imgPublishes.append(dst)
				
				except Exception as e: 
					errorMessage.append('Failed to copy %s-%s' % (src, dst))

			info.set('primaryOutput', 'publishImgFiles', imgPublishes)


			# copy to heroImgSrc 
			imgExt = os.path.splitext(heroImgSrc)[-1]
			heroImgDst = '%s/%s%s' % (mediaPath, publishName, imgExt)
			heroPreview = '%s/%s%s' % (mediaPath, entity.name, imgExt)
			
			if heroImgSrc: 
				try: 
					file_utils.copy(heroImgSrc, heroImgDst)
					logger.debug('Copy to hero %s - %s' % (heroImgSrc, heroImgDst))
					imgPublishes.append(heroImgDst)
					info.set('primaryOutput', 'heroImgFile', str(heroImgDst))

				except Exception as e: 
					errorMessage.append('Failed to copy to hero %s-%s' % (heroImgSrc, heroImgDst))

				# copy to preview file
				try: 
					file_utils.copy(heroImgSrc, heroPreview)
					logger.debug('Copy to master %s - %s' % (heroImgSrc, heroPreview))
					imgPublishes.append(heroPreview)

				except Exception as e: 
					errorMessage.append('Failed to copy to master %s-%s' % (heroImgSrc, heroPreview))

			# copy to heroMovSrc 
			if heroMovSrc: 	
				movExt = os.path.splitext(heroMovSrc)[-1]
				heroMovDst = '%s/%s%s' % (mediaPath, publishName, movExt)
				try: 
					file_utils.copy(heroMovSrc, heroMovDst)
					logger.debug('Copy to hero %s - %s' % (heroMovSrc, heroMovDst))
					imgPublishes.append(heroMovDst)
					info.set('primaryOutput', 'heroMovFile', heroMovDst)

				except Exception as e: 
					errorMessage.append('Failed to copy to hero %s-%s' % (heroMovSrc, heroMovDst))

			else: 
				# if not media, use image as upload media
				info.set('primaryOutput', 'heroMovFile', str(heroImgDst))


	if errorMessage: 
		return False, errorMessage

	else: 
		return True, 'Success \n%s' % imgPublishes




def save_file(entity=None): 
	""" save increment file to lock wip version """
	errorMessage = []
	
	if not entity: 
		entity = path_info.PathInfo()

	if entity: 
		logger.debug('start publishing ...')

		# get publish info 
		publishFile, saveWorkFile, incrementSaveWorkFile, libFile = pub_utils.get_publish_info(entity)
		
		logger.debug('save work file %s' % saveWorkFile)
		logger.debug('publish version %s' %  publishFile)
		logger.debug('save increment work file %s' % incrementSaveWorkFile)

		# start process files 
		saveResult = None
		workResult = None

		# publish info 
		pubEntity = path_info.PathInfo(publishFile)
		info = publish_info.TaskInfo(pubEntity)

		# save as
		saveResult = hook.save_file_as(incrementSaveWorkFile)
		info.set('work', 'incrementWorkFile', incrementSaveWorkFile)

		if saveResult: 
			# copy to current work version (short cut for overwritten save)
			workResult = file_utils.copy(saveResult, saveWorkFile)
			info.set('work', 'workfile', saveWorkFile)


		if not saveResult: 
			logger.error('Save to %s has failed' % incrementSaveWorkFile)
			errorMessage.append('Save to %s has failed' % incrementSaveWorkFile)

		if not workResult: 
			logger.error('Overwrite work version %s has failed' % saveWorkFile)
			errorMessage.append('Overwrite work version %s has failed' % saveWorkFile)

	if errorMessage: 
		return False, errorMessage

	else: 
		return True, 'Success \n%s' % workResult