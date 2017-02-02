import sys
import os
import platform
import logging

logger = logging.getLogger(__name__)

if os.environ.get('RFSCRIPT', False):
	path = '%s/config' % os.environ.get('RFSCRIPT')
	if not path in sys.path:
		sys.path.append(path)

import config
from shotgun_api3 import Shotgun
from rftool.utils import path_info
reload(path_info)

# connection to server
server = config.server
script = config.script
id = config.id
sg = Shotgun(server, script, id)

class SGEntity(object):
	"""docstring for SGEntity"""
	def __init__(self, path=None):
		super(SGEntity, self).__init__()

		self.pathInfo = None

		if type(path).__name__ == 'PathInfo':
			self.pathInfo = path
		elif type(path).__name__ == 'str':
			self.pathInfo = path_info.PathInfo(path)

		# cache
		self.cacheProject = None
		self.cacheEntity = None
		self.cacheTasks = None

	def __str__(self):
		return self.pathInfo

	def __repr__(self):
		return str(self.pathInfo)

	@property
	def entity(self):
		if not self.cacheEntity:
			if self.pathInfo.entity == path_info.config.asset:
				entity = 'Asset'
				fields = ['id', 'code', 'sg_type', 'sg_subtype']

			if self.pathInfo.entity == path_info.config.shot:
				entity = 'Shot'
				fields = ['id', 'code']

			entityName = self.pathInfo.name
			fields.append('sg_status_list')
			fields.append('project')
			filters = [['project.Project.name', 'is', self.pathInfo.project],
						['code', 'is', entityName]]
			self.cacheEntity = sg.find_one(entity, filters=filters, fields=fields)

		return self.cacheEntity

	@property
	def project(self):
		if not self.cacheProject:
			self.cacheProject = sg.find_one('Project', [['name', 'is', self.pathInfo.project]], ['name', 'id'])
		return self.cacheProject

	@property
	def id(self):
		entity = self.entity
		return entity.get('id')

	@property
	def tasks(self):
		entity = self.entity
		if not self.cacheTasks:
			filters = [['project', 'is', entity['project']]
						['entity', 'is', entity]]
			fields = ['content', 'sg_status_list', 'entity', 'task_assignees']
			self.cacheTasks = sg_find('Task', filters=filters, fields=fields)
		return self.cacheTasks

	def get_project(self, project):
		return sg.find_one('Project', [['name', 'is', project]], ['name', 'id'])

	def get_template(self, template):
		return sg.find_one('TaskTemplate', [['code', 'is', template]], ['code', 'id'])

	def create(self, project='', entity='', name='', assetType='', assetSubType='', episode='', sequence='', template=''):
		projectEntity = self.get_project(project)
		templateEntity
		data = {'project': projectEntity, 'code': name, 'task_template': template}
		if entity == 'Asset':
			data.update({'sg_asset_type': assetType, 'sg_subtype': assetSubType})
			sg.create(entity, data)



