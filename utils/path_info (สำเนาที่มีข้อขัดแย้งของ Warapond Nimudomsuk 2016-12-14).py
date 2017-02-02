import os
import sys
import logging
logger = logging.getLogger()


from startup import config
reload(config)

try:
	import maya.cmds as mc
	import maya.mel as mm
	isMaya = True

except ImportError:
	isMaya = False

class PathInfo(object):
	"""docstring for PathInfo"""
	def __init__(self, path=None, **kwarg):
		super(PathInfo, self).__init__()

		# get current scene
		if not path and isMaya:
			path = mc.file(q=True, loc=True)
		self.path = path
		self.input = 'path'

		# construct path
		if kwarg:
			self.path = self.construct_path(kwarg)
			self.input = 'entity'

		# cache variable
		self.cacheProjectCode = None

	def __str__(self):
		return self.path

	def __repr__(self):
		return self.path

	def construct_path(self, entity):
		''' entity expect {'project': 'project', 'entity'='asset', entitySub1='character', entitySub2='main', name='aiya', step=model}'''
		pathElems = []
		pathElems.append(self.root)
		pathElems.append((entity.get('project', 'none')))
		pathElems.append((entity.get('entity', 'none')))
		pathElems.append((entity.get('entitySub1', 'none')))
		pathElems.append((entity.get('entitySub2', 'none')))
		pathElems.append((entity.get('name', 'none')))
		pathElems.append((entity.get('step', 'none')))

		logger.debug('Object were construct with %s' % self.path)
		return ('/').join(pathElems)

	@property
	def valid(self):
		if self.root in self.path:
			if len(self.projPath.split('/')) >= 6:
				return True

	@property
	def root(self):
		return os.environ.get('RFPROJECT', '').replace('\\', '/')

	@property
	def rootPubl(self):
		return os.environ.get('RFPUBL', '').replace('\\', '/')

	@property
	def rootProd(self):
		return os.environ.get('RFPROD', '').replace('\\', '/')

	@property
	def projPath(self):
		if '$RFPROJECT' in self.path:
			return self.path.replace('$RFPROJECT/', '')
		if '$RFPUBL' in self.path:
			return self.path.replace('$RFPUBL/', '')
		if '$RFPROD' in self.path:
			return self.path.replace('$RFPROD/', '')
		if self.root in self.path:
			return self.path.replace('%s/' % self.root, '')
		if self.rootPubl in self.path:
			return self.path.replace('%s/' % self.rootPubl, '')
		if self.rootProd in self.path:
			return self.path.replace('%s/' % self.rootProd, '')

	@property
	def absPath(self):
		if '$RFPROJECT' in self.path:
			return self.path.replace('$RFPROJECT', os.environ[config.RFPROJECT])
		if '$RFPUBL' in self.path:
			return self.path.replace('$RFPUBL', os.environ[config.RFPUBL])
		if '$RFPROD' in self.path:
			return self.path.replace('$RFPROD', os.environ[config.RFPROD])
		return self.path


	@property
	def project(self):
		return self.projPath.split('/')[0]

	@property
	def entity(self):
		return self.projPath.split('/')[1]

	@property
	def type(self):
		return self.projPath.split('/')[2]

	@property
	def subtype(self):
		return self.projPath.split('/')[3]

	@property
	def asset(self):
		return self.projPath.split('/')[4]


	@property
	def step(self):
		return self.projPath.split('/')[5]

	@property
	def workspace(self):
		return self.projPath.split('/')[6]

	@property
	def filename(self):
		return os.path.basename(self.path)

	@property
	def fileUser(self):
		return os.path.splitext(self.path)[0].split('/')[-1]

	@property
	def episode(self):
		return self.projPath.split('/')[2]

	@property
	def sequence(self):
		return self.projPath.split('/')[3]

	@property
	def shot(self):
		return self.projPath.split('/')[4]

	@property
	def projectCode(self):
		if not self.cacheProjectCode:
			from rftool.utils import sg_hook
			result = sg_hook.sg.find_one('Project', [['name', 'is', self.project]], ['sg_project_code'])
			if result:
				self.cacheProjectCode = result['sg_project_code']

		return self.cacheProjectCode

	@property
	def name(self):
		if self.entity == config.asset:
			return self.assetName()

		if self.entity == config.scene:
			return self.shotName()

	def workspaceDir(self, root='RFPROJECT'):
		return config.workDir.get(root, '')

	def workspacePath(self, root='RFPROJECT', relativePath=False):
		projRoot = os.environ.get(root, '')
		if relativePath:
			projRoot = '$%s' % (root)

		return '{0}/{1}/{2}/{3}/{4}/{5}/{6}/{7}'.format(projRoot, self.project, self.entity, self.type, self.subtype, self.name, self.step, self.workspaceDir(root))


	def assetName(self, project=False, step=False):
		nameEles = []
		if project:
			nameEles.append(self.projectCode)

		nameEles.append(self.asset)

		if step:
			nameEles.append(self.step)
		return '_'.join(nameEles)

	def shotName(self, step=False):
		nameEles = [self.projectCode, self.episode, self.sequence, self.shot]
		if step:
			nameEles.append(self.step)
		return '_'.join(nameEles)


# example
# asset = path_info.PathInfo(project='project', entity='asset', entitySub1='character', entitySub2='main', name='aiya', step='rig')

# asset.workSpacePath(root='RFPROJECT', relativePath=True)
# Result: $RFPROJECT/project/asset/character/main/aiya/rig #

# asset.workSpacePath(root='RFPROJECT', relativePath=False)
# Result: C:/Users/TA/Dropbox/projects/Riff/double_monkey/project_server/project/asset/character/main/aiya/rig #


