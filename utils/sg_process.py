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

# connection to server
server = config.server
script = config.script
id = config.id
sg = Shotgun(server, script, id)

################# find/find_one ###################

def get_projects():
	return sg.find('Project', [], ['name', 'id', 'sg_project_code'])

def get_one_project(project):
	filters = [['project.Project.name', 'is', project]]
	fields = ['code', 'id']
	return sg.find_one('Project', filters, fields)

def get_episodes(project):
	filters = [['project.Project.name', 'is', project]]
	fields = ['code', 'id', 'shortCode']
	return sg.find('Scene', filters, fields)

def get_one_episode(project,episode):
	filters = [['project.Project.name', 'is', project],
				['code', 'is', episode]]
	fields = ['code', 'id']
	return sg.find_one('Scene', filters, fields)

def get_sequences(project, episode):
	filters = [['project', 'is', project], ['sg_episode', 'is', episode]]
	fields = ['code', 'id', 'sg_shortcode']
	return sg.find('Sequence', filters, fields)

def get_one_sequence(project, episode, sequence):
	filters = [['project.Project.name', 'is', project],
				['sg_episode.Scene.code', 'is', episode],
				['code', 'is', sequence]]
	fields = ['code', 'id']
	return sg.find_one('Sequence', filters, fields)

def get_shots(project, episode, sequence):
	filters = [['project', 'is', project], ['sg_episode', 'is', episode], ['sg_sequence', 'is', sequence]]
	fields = ['code', 'id', 'sg_shortcode', 'sg_episode', 'sg_sequence', 'sg_sequence.Sequence.sg_shortcode']
	return sg.find('Shot', filters, fields)

def get_one_shot(project, episode, sequence, shot):
	filters = [	['project.Project.name', 'is', project],
				['sg_episode.Scene.code', 'is', episode],
				['sg_sequence.Sequence.sg_shortcode', 'is', sequence],
				['sg_shortcode', 'is', shot]]
	fields = ['code', 'id', 'sg_shortcode', 'sg_episode', 'sg_sequence', 'sg_sequence.Sequence.sg_shortcode']
	return sg.find_one('Shot', filters, fields)

def get_shot_entity(project, code):
	filters = [	['project.Project.name', 'is', project], ['code', 'is', code]]
	fields = ['code', 'id', 'sg_shortcode', 'sg_episode', 'sg_sequence', 'sg_sequence.Sequence.sg_shortcode']
	return sg.find_one('Shot', filters, fields)

def get_subtype():
	return sg.schema_field_read('Asset', 'sg_subtype')['sg_subtype']["properties"]["valid_values"]["value"]

def get_type():
	return sg.schema_field_read('Asset', 'sg_asset_type')['sg_asset_type']["properties"]["valid_values"]["value"]

def get_assets(project):
	filters = [['project.Project.name', 'is', project]]
	fields = ['code', 'sg_asset_type', 'sg_subtype', 'sg_episodes']
	return sg.find('Asset', filters, fields)

def get_one_asset(project,assetName):
	filters = [ ['project.Project.name','is',project],
				['code','is',assetName] ]
	fields = ['code', 'sg_asset_type', 'sg_subtype', 'sg_episodes']
	return sg.find_one('Asset',filters,fields)

def get_step():
	filters = []
	fields = ['code', 'id', 'entity_type']
	return sg.find('Step', filters, fields)

def get_task(entityType, userEntity, projectEntity, episodeEntity, stepEntity):
	filters = taskFilters(entityType, userEntity, projectEntity, episodeEntity, stepEntity)
	fields = taskFields(entityType)
	return sg.find('Task', filters, fields)

def get_tasks(entity):
	filters = [['entity', 'is', entity]]
	fields = ['content', 'id', 'project', 'sg_status_list', 'task_assignees', 'step', 'sg_app', 'sg_resolution']
	return sg.find('Task', filters, fields)

def get_tasks_by_step(entity, step):
	filters = [['entity', 'is', entity], ['step.Step.code', 'is', step]]
	fields = ['content', 'id', 'project', 'sg_status_list', 'task_assignees', 'step', 'sg_app', 'sg_resolution']
	return sg.find('Task', filters, fields)

def get_one_task(entity,task):
	filters = [ ['entity','is',entity],
				['content','is',task]]
	fields = taskFields(entity['type'])
	return sg.find_one('Task', filters, fields)

def get_one_version(version):
	return sg.find_one('Version', [['code', 'is', version]], ['code', 'id', 'sg_status_list'])

def get_users():
	fields = ['name', 'id', 'sg_localuser', 'groups']
	users = sg.find('HumanUser', [], fields)

	return users

def get_list_field(field) :
	# name to add to the list
	#type = 'sg_subtype' for supType
	#type = 'sg_asset_type' for Type

	values = sg.schema_field_read(str('Asset'), str(field)) [str(field)]["properties"]["valid_values"]["value"]
	return values

####################### create ########################

def create_asset(project, assetType, assetSubType, assetName, episode=None, template='default', taskTemplate=None):
	if not taskTemplate:
		if template == 'default':
			taskTemplate = {'code': 'th_ch_asset_md_template', 'type': 'TaskTemplate', 'id': 110}
		if template == 'lo':
			taskTemplate = {'code': 'dm_asset_pxy_template', 'type': 'TaskTemplate', 'id': 77}
		if template == 'hi':
			taskTemplate = {'code': 'dm_asset_hi_template', 'type': 'TaskTemplate', 'id': 76}

	data = dict()
	if episode:
		data.update({'sg_episodes': episode})

	add_list_field(assetType, 'sg_asset_type')
	add_list_field(assetSubType, 'sg_subtype')

	data.update({'project': project, 'sg_asset_type': assetType, 'sg_subtype': assetSubType, 'code': assetName, 'task_template': taskTemplate})
	return sg.create('Asset', data)


def create_episode(project, episodeName):
	data = {'project': project, 'code': episodeName}
	return sg.create('Scene', data)

def create_sequence(project, episode, sequenceName, shortCode):
	result = get_one_sequence(project.get('name'), episode.get('code'), sequenceName)
	if not result:
		projCode = project.get('sg_project_code')
		data = {'project': project, 'sg_episode': episode, 'sg_shortcode': shortCode, 'code': sequenceName}
		result = sg.create('Sequence', data)

	return result

def create_shot(project, episode, sequence, shotName, shortCode, template='default', taskTemplate=None, startFrame=None, endFrame=None, duration=None):
	result = sg.find_one('Shot', [['project', 'is', project], ['code', 'is', shotName]], ['id', 'code'])
	if not result:
		if not taskTemplate:
			if template == 'default':
				taskTemplate = {'code': 'dm_shot_template', 'type': 'TaskTemplate', 'id': 78}

		projCode = project.get('sg_project_code')
		data = {'project': project, 'sg_episode': episode, 'sg_sequence': sequence, 'sg_shortcode': shortCode, 'code': shotName, 'task_template': taskTemplate}
		if startFrame and endFrame:
			data.update({'sg_cut_in': startFrame, 'sg_cut_out': endFrame, 'sg_cut_duration': duration})
		result = sg.create('Shot', data)

	return result


########################### Update ##########################

def link_local_user(userId, localUser):
	return sg.update('HumanUser', userId, {'sg_localuser': localUser})

def set_task_status(taskId, status):
	return sg.update('Task', taskId, {'sg_status_list': status})

def set_entity_status(entity, entityId, status):
	return sg.update(entity, entityId, {'sg_status_list': status})

def assign_task(taskId, userId):
	return sg.update('Task', taskId, {'task_assignees': [{'type': 'HumanUser', 'id': userId}]})

########################### Other ###########################

def add_list_field(name, field) :
	# name to add to the list
	#type = 'sg_subtype' for supType
	#type = 'sg_asset_type' for Type

	values = sg.schema_field_read(str('Asset'), str(field)) [str(field)]["properties"]["valid_values"]["value"]
	if not name in values :
		values.append(name)
		properties = {'valid_values' : values}
		sg.schema_field_update(str('Asset'), str(field), properties)
		return values

def remove_list_field(name, field):
	values = sg.schema_field_read(str('Asset'), str(field)) [str(field)]["properties"]["valid_values"]["value"]
	if name in values :
		values.remove(name)
		properties = {'valid_values' : values}
		sg.schema_field_update(str('Asset'), str(field), properties)
		return values

def taskFilters(entityType, userEntity, projectEntity, episodeEntity, stepEntity) :

	filters = [['task_assignees', 'is', userEntity], ['step', 'is', stepEntity], ['project', 'is', projectEntity]]
	advancedFilter1 = {
						"filter_operator": "any",
						"filters": [
						["sg_status_list", "is", "ip"],
						["sg_status_list", "is", "rdy"],
						["sg_status_list", "is", "wtg"],
						["sg_status_list", "is", "apr"],
						["sg_status_list", "is", "rev"],
						["sg_status_list", "is", "fix"],
						]
					}

	filters.append(advancedFilter1)

	if not episodeEntity['code'] == '-' :

		if entityType == 'Asset' :
			filters.append(['entity.Asset.scenes', 'is', episodeEntity])

		if entityType == 'Shot' :
			filters.append(['entity.Shot.sg_scene', 'is', episodeEntity])

	return filters

def taskFields(entityType) :
	fields = ['content', 'entity', 'step', 'project', 'sg_status_list', 'task_assignees', 'sg_app', 'sg_resolution']
	assetFields = ['entity.Asset.code', 'entity.Asset.sg_asset_type', 'entity.Asset.sg_subtype', 'entity.Asset.scenes']
	shotFields = ['entity.Shot.code', 'entity.Shot.sg_sequence', 'entity.Shot.sg_scene', 'entity.Shot.sg_scene']

	if entityType == 'Asset' :
		fields = fields + assetFields

	if entityType == 'Shot' :
		fields = fields + shotFields
	return fields