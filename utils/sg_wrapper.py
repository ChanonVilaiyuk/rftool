import sys
import os
import platform
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

if os.environ.get('RFSCRIPT', False):
	path = '%s/config' % os.environ.get('RFSCRIPT')
	print path
	if not path in sys.path:
		sys.path.append(path)

from shotgun_api3 import Shotgun
import config

# connection to server
server = config.server
script = config.script
id = config.id
sg = Shotgun(server, script, id)

def get_projects():
	return sg.find('Project', [], ['name', 'id'])

def get_project_entity(project):
	return sg.find_one('Project', [['name', 'is', project]], ['name', 'id'])

def get_template(template):
	return sg.find_one('TaskTemplate', [['code', 'is', template]], ['code', 'id'])

def create(project='', entity='', name='', assetType='', assetSubType='', episode='', sequence='', template=''):
	projectEntity = get_project_entity(project)
	templateEntity = get_template(template)
	if projectEntity and name:
		data = {'project': projectEntity, 'code': name, 'task_template': templateEntity}

		if entity == 'Asset':
			data.update({'sg_asset_type': assetType, 'sg_subtype': assetSubType})
		if entity == 'Shot':
			data.update({'sg_asset_type': assetType, 'sg_subtype': assetSubType})


def create_asset(data):
	return sg.create('Asset', data)

def create_version(data):
	return sg.create('Version',data)

def upload_thumbnail(entity,imgpath):
	print sg.upload_thumbnail(entity['type'],entity['id'],imgpath)

def upload_movie(entity,moviepath):
	print sg.upload(entity['type'],entity['id'],moviepath,field_name='sg_uploaded_movie',display_name=moviepath.split('/')[-1].split('.')[0])

def set_task_status(taskId, data):
	return sg.update('Task', taskId, data)

def get_version_entity(version):
	return sg.find_one('Version', [['code', 'is', version]], ['code', 'id'])

def update_version_entity(entid,data):
	return sg.update('Version',entid,data)


class SGEntity(object):
	"""docstring for SGEntity"""
	def __init__(self, entityType='', project='', entityName='', filters=[], fields=['id', 'code'], entityDict=None):
		super(SGEntity, self).__init__()
		# cache
		self.projectDict = dict()
		self.taskDict = dict()
		self.updateDict = dict()
		self.stepDict = dict()
		self.userDict = dict()

		# default setting
		self.projectFields = ['name', 'id', 'sg_shortcode']
		self.assetFields = ['code', 'id', 'sg_asset_type', 'sg_subtype', 'sg_status_list']
		self.taskFields = ['content', 'id', 'entity', 'sg_status_list', 'step', 'task_assignees']
		self.stepFields = ['code', 'id']
		self.userFields = ['name', 'id']

		# default
		self.entityType = entityType
		self.project = project
		self.entityName = entityName
		self.filters = filters
		self.fields = fields
		self.entityDict = dict()

		if not entityDict:
			self.entityDict = self.get_entity()
		else:
			if type(entityDict) == type(dict()):
				self.entityDict = entityDict
			else:
				logger.error('Input entityDict is not a valid dictionary')


	def get_entity(self):
		filters = []
		fields = []

		projectDict = self.get_project()
		if projectDict:
			filters = [['project', 'is', projectDict]]
			if self.filters:
				filters = filters + self.filters

		if self.entityType == 'Asset':
			filters.append(['code', 'is', self.entityName])

			fields = self.assetFields
			if self.fields:
				fields = fields + self.fields

		if self.entityType == 'Task':
			filters.append(['content', 'is', self.entityName])

			fields = self.assetFields
			if self.fields:
				fields = fields + self.fields

		entity = sg.find(self.entityType, filters, fields)
		if entity:
			if len(entity) > 1:
				logger.warning('More than 1 name for %s' % self.entityName)
				logger.warning(str([a['id'] for a in entity]))
			return entity[0]
		else:
			logger.warning('No entity name "%s" found on shotgun' % self.entityName)
			return dict()

	def get_project(self):
		if self.projectDict:
			return self.projectDict
		else:
			projectDict = sg.find_one('Project', [['name', 'is', self.project]], self.projectFields)
			if projectDict:
				self.projectDict = projectDict
				return projectDict
			else:
				logger.warning('No project found %s' % self.project)

	@property
	def id(self):
		if self.entityDict:
			return self.entityDict.get('id')
		logger.warning('No id found')
		return 0


	@property
	def tasks(self):
		if self.entityDict:
			if self.entityDict.get('type') in ['Asset', 'Shot', 'Sequence']:
				entityDict = self.entityDict

			if self.entityDict.get('type') == 'Task':
				entityDict = self.entityDict.get('entity')

			if not self.taskDict:
				taskDict = sg.find('Task', [['entity', 'is', entityDict]], self.taskFields)
				if taskDict:
					self.taskDict = taskDict
					return taskDict
				else:
					logger.warning('No task found for %s' % self.entityName)

			else:
				return self.taskDict

		else:
			logger.warning('Cannot get task. No entity name "%s"' % self.entityName)

	def set_update(self, updateDict, mode='w'):
		if mode == 'w':
			self.updateDict = updateDict
		if mode == 'a':
			self.updateDict.update(updateDict)

	def update(self):
		entityId = self.entityDict.get('id')
		if entityId:
			result = sg.update(self.entityType, entityId, self.updateDict)
			return result
		else:
			logger.warning('There is no entity id for %s' % self.entityName)

	def create(self, entityType, entityName):
		if self.entityDict.get('type') in ['Asset', 'Shot', 'Sequence']:
			updateDict = {'project': self.projectDict, 'entity': self.entityDict}
			if entityType == 'Task':
				updateDict.update({'content': entityName})
			elif entityType == 'Version':
				updateDict.update({'code': entityName})
			else:
				logger.warning('You cannot create "%s" with this instance type of "%s"' % (entityType, self.entityDict.get('type')))

			if self.updateDict:
				updateDict.update(self.updateDict)

			result = sg.create(entityType, updateDict)
			return result


	def create_task(self):
		return self.create('Task')

	def steps(self, name=''):
		if not self.stepDict:
			self.stepDict = sg.find('Step', [], self.stepFields)
		if not name:
			return self.stepDict
		else:
			print self.stepDict
			return [a for a in self.stepDict if a['code'] == name]

	def users(self, name=''):
		if not self.userDict:
			self.userDict = sg.find('HumanUser', [], self.userFields)
		if not name:
			return self.userDict
		else:
			return [a for a in self.userDict if a['name'] == name]

