import sys, os
import logging

logger = logging.getLogger(__name__)

from startup import config
from startup import template
from rftool.utils import path_info
from rftool.utils import file_utils


def create_asset_template(root, project, assetType, assetSubType, assetName):
	scriptServer = os.environ['RFSCRIPT']
	templatePath = ''
	rootValid = False

	if root == config.RFPROJECT:
		steps = template.workAssetSteps
		templatePath = '%s/RFPROJECT' % template.templatePath
		rootValid = True

	if root == config.RFPUBL:
		steps = template.publAssetSteps
		templatePath = '%s/RFPUBL' % template.templatePath
		rootValid = True

	if root == config.RFPROD:
		steps = template.prodAssetSteps
		templatePath = '%s/RFPROD' % template.templatePath
		rootValid = True

	if rootValid:
		asset = path_info.PathInfo(project=project, entity=config.asset, entitySub1=assetType, entitySub2=assetSubType, name=assetName)
		assetPath = asset.entityPath(root)

		if not os.path.exists(assetPath):
			os.makedirs(assetPath)

		for step in steps:
			src = '%s/%s' % (templatePath, step)
			dst = '%s/%s' % (assetPath, step)
			result = file_utils.copyTree(src, dst)
			logger.debug('Copy %s -> %s success' % (src, dst))

		create_standin(asset)
		repath_ad(asset)

		return True

def create_scene_template(root, project, episodeName, sequenceName, shotName):
	scriptServer = os.environ['RFSCRIPT']
	templatePath = ''
	rootValid = False

	if root == config.RFPROJECT:
		steps = template.workSceneSteps
		templatePath = '%s/RFPROJECT' % template.templatePath
		rootValid = True

	if root == config.RFPUBL:
		steps = template.publSceneSteps
		templatePath = '%s/RFPUBL' % template.templatePath
		rootValid = True

	if root == config.RFPROD:
		steps = template.prodSceneSteps
		templatePath = '%s/RFPROD' % template.templatePath
		rootValid = True

	if rootValid:
		shot = path_info.PathInfo(project=project, entity=config.scene, entitySub1=episodeName, entitySub2=sequenceName, name=shotName)
		shotPath = shot.entityPath(root)

		if not os.path.exists(shotPath):
			os.makedirs(shotPath)

		for step in steps:
			src = '%s/%s' % (templatePath, step)
			dst = '%s/%s' % (shotPath, step)
			result = file_utils.copyTree(src, dst)
			logger.debug('Copy %s -> %s success' % (src, dst))

		return True


def create_standin(asset):
	assetPath = asset.entityPath('RFPROJECT')
	refPath = '%s/%s' % (assetPath, config.ref)
	files = file_utils.listFile(refPath)
	count = 0

	if files:
		for ref in files:
			if config.libFileReplaceKw in ref:
				newName = ref.replace(config.libFileReplaceKw, asset.name)
				src = '%s/%s' % (refPath, ref)
				dst = '%s/%s' % (refPath, newName)
				os.rename(src, dst)
				logger.debug('Renaming %s -> %s' % (src, dst))
				count+=1

	logger.info('renaming %s files standin complete (%s)' % (count, refPath))


def repath_ad(asset):
	assetPath = asset.entityPath('RFPROJECT')
	refPath = '%s/%s' % (assetPath, config.ref)
	files = file_utils.listFile(refPath)
	adFile = asset.libName('', 'ad', project=False)
	replaceDict = {config.assemblyMap['assetName']: '%s_ad' % asset.name, config.assemblyMap['locatorLabel']: asset.name}

	if os.path.exists('%s/%s' % (refPath, adFile)):

		if files:
			for k, v in config.representationMap.iteritems():
				replaceFile = [a for a in files if k in a]

				if replaceFile:
					path = '%s/%s' % (refPath, replaceFile[0])
					replaceDict.update({v: path})

			logger.debug('replaceKey %s' % str(replaceDict))
			logger.info('repath ad complete %s' % ('%s/%s' % (refPath, adFile)))
			return file_utils.search_replace_keys('%s/%s' % (refPath, adFile), replaceDict, backupFile=False)
