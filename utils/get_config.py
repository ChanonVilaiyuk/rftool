
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from startup import config
from rftool.utils import sg_process
from rftool.utils import file_utils

def getProjectConfig():
	return sg_process.get_projects()

def getProjectNames():
	projects = getProjectConfig()
	return sorted([a['name'] for a in projects])

def allTypes(mode_path = ''):

	if mode_path:
		return file_utils.listFolder(mode_path)

def allSubtypes(mode_path = ''):
	subs = []

	if mode_path:
		for typ in file_utils.listFolder(mode_path):
			typ_path = mode_path + '/' + typ
			for sub in file_utils.listFolder(typ_path):
				if not sub in subs:
					subs.append(sub)

		return subs