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
