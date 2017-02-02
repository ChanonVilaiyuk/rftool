import sys
import os
import platform
import logging

logger = logging.getLogger(__name__)

if os.environ.get('RFSCRIPT', False):
	path = '%s/config' % os.environ.get('RFSCRIPT')
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