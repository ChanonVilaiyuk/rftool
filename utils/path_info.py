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
        self.activeApp = 'maya'
        if not path and isMaya:
            path = mc.file(q=True, loc=True)
            self.activeApp = 'maya'
        self.path = path
        self.input = 'path'
        self.task = ''

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
        ''' entity expect {'project': 'project', 'entity'='asset', entitySub1='character', entitySub2='main', name='aiya', step=model, task='model_md'}'''
        ''' entity expect {'project': 'project', 'entity'='scene', entitySub1='ep1', entitySub2='q0010', name='s0010', step=model, task='model_md'}'''
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
    def relPath(self):
        if os.environ.get(config.RFPROJECT) in self.path:
            return self.path.replace(os.environ.get(config.RFPROJECT), '$RFPROJECT')
        if os.environ.get(config.RFPUBL) in self.path:
            return self.path.replace(os.environ.get(config.RFPUBL), '$RFPUBL')
        if os.environ.get(config.RFPROD) in self.path:
            return self.path.replace(os.environ.get(config.RFPROD), '$RFPROD')
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
    def application(self):
        return self.projPath.split('/')[6]

    @property
    def workspace(self):
        return self.projPath.split('/')[7]

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def taskName(self):
        versionKey = '_v'
        if versionKey in self.filename:
            task = self.filename.split(versionKey)[0].replace('%s_' % self.name, '')
        else:
            task = self.filename.split('.')[0].replace('%s_' % self.name, '')

        self.task = task
        return task

    @property
    def versionName(self):
        basename = os.path.basename(self.path).split('.')[0]
        if not basename.split('_')[-1][0] == 'v' and not basename.split('_')[-1][1:].isdigit():
            name = basename.replace('_%s' % basename.split('_')[-1], '')
            return name
        else:
            return os.path.basename(self.path).split('.')[0]

    @property
    def fileUser(self):
        return os.path.splitext(self.path)[0].split('/')[-1]

    @property
    def user(self):
        basename = os.path.basename(self.path).split('.')[0]
        if not basename.split('_')[-1][0] == 'v' and not basename.split('_')[-1][1:].isdigit():
            return basename.split('_')[-1]

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
            return self.shotName(fullName=False)

    @property
    def versionNoUser(self):
        return '_'.join(os.path.basename(self.path).split('.')[0].split('_')[:-1])

    def entity1Path(self):
        # projRoot = os.environ.get(root, '')
        return '{0}/{1}/{2}/{3}'.format(self.root, self.project, self.entity, self.type)

    def entity2Path(self):
        # projRoot = os.environ.get(root, '')
        return '{0}/{1}/{2}/{3}/{4}'.format(self.root, self.project, self.entity, self.type, self.subtype)

    def entityPath(self, root='RFPROJECT'):
        projRoot = os.environ.get(root, '')
        return '{0}/{1}/{2}/{3}/{4}/{5}'.format(projRoot, self.project, self.entity, self.type, self.subtype, self.name)

    def libPath(self, root='RFPROJECT'):
        projRoot = os.environ.get(root, '')
        return '{0}/{1}/{2}/{3}/{4}/{5}/{6}'.format(projRoot, self.project, self.entity, self.type, self.subtype, self.name, config.ref)

    def workspaceDir(self, root='RFPROJECT'):
        return config.workDir.get(root, '')

    def workspacePath(self, root='RFPROJECT', relativePath=False):
        projRoot = os.environ.get(root, '')
        if relativePath:
            projRoot = '$%s' % (root)

        return '{0}/{1}/{2}/{3}/{4}/{5}/{6}/{7}/{8}'.format(projRoot, self.project, self.entity, self.type, self.subtype, self.name, self.step, self.activeApp, self.workspaceDir(root))

    def stepPath(self, root='RFPROJECT', relativePath=False):
        projRoot = os.environ.get(root, '')
        if relativePath:
            projRoot = '$%s' % (root)

        return '{0}/{1}/{2}/{3}/{4}/{5}/{6}'.format(projRoot, self.project, self.entity, self.type, self.subtype, self.name, self.step)

    def assetName(self, project=False, step=False):
        nameEles = []
        if project:
            nameEles.append(self.projectCode)

        nameEles.append(self.asset)

        if step:
            nameEles.append(self.step)

        return '_'.join(nameEles)

    def libName(self, step, res):
        return '{0}.{1}'.format('_'.join([self.assetName(project=True), step, res]), config.refExt)

    def getRefs(self):
        if os.path.exists(self.libPath()):
            files = listFile(self.libPath())
            return [a for a in files if os.path.splitext(a)[-1] == '.%s' % config.refExt]

    def shotName(self, project=False, step=False, fullName=True):
        nameElems = []
        if fullName:
            if project:
                nameElems.append(self.projectCode)

            nameElems = nameElems + [self.episode, self.sequence, self.shot]
            if step:
                nameElems.append(self.step)
            return '_'.join(nameElems)
        else:
            return self.shot

    def sequenceName(self, project=False, step=False, fullName=True):
        nameElems = []
        if fullName:
            if project:
                nameElems.append(self.projectCode)

            nameElems = nameElems + [self.episode, self.sequence]
            if step:
                nameElems.append(self.step)
            return '_'.join(nameElems)
        else:
            return self.sequence

def convertAbs(path):
    if '$RFPROJECT' in path:
        return path.replace('$RFPROJECT', os.environ[config.RFPROJECT])
    if '$RFPUBL' in path:
        return path.replace('$RFPUBL', os.environ[config.RFPUBL])
    if '$RFPROD' in path:
        return path.replace('$RFPROD', os.environ[config.RFPROD])
    return path

def convertRel(path):
    if os.environ.get(config.RFPROJECT) in path:
        return path.replace(os.environ.get(config.RFPROJECT), '$RFPROJECT')
    if os.environ.get(config.RFPUBL) in path:
        return path.replace(os.environ.get(config.RFPUBL), '$RFPUBL')
    if os.environ.get(config.RFPROD) in path:
        return path.replace(os.environ.get(config.RFPROD), '$RFPROD')
    return path

def convertRoot(path, root='RFPROJECT', absPath=True):
    envs = ['$RFPROJECT', '$RFPUBL', '$RFPROD']
    absEnvs = [config.rootWork, config.rootPubl, config.rootProd]
    projPath = ''

    for env in envs:
        if env in path:
            projPath = path.replace(env, '')

    for absEnv in absEnvs:
        if absEnv in path:
            projPath = path.replace(absEnv, '')

    if projPath:
        if absPath:
            return '%s%s' % (os.environ.get(root), projPath)
        return '$%s%s' % (root, projPath)

def guess_res(filename):
    name = os.path.splitext(filename)[0]
    lastElem = name.split('_')[-1]
    if lastElem in config.res:
        return lastElem

def listFile(path):
    return [a for a in os.listdir(path) if os.path.isfile(os.path.join(path, a))]


# example
# asset = path_info.PathInfo(project='project', entity='asset', entitySub1='character', entitySub2='main', name='aiya', step='rig')

# asset.workSpacePath(root='RFPROJECT', relativePath=True)
# Result: $RFPROJECT/project/asset/character/main/aiya/rig #

# asset.workSpacePath(root='RFPROJECT', relativePath=False)
# Result: C:/Users/TA/Dropbox/projects/Riff/double_monkey/project_server/project/asset/character/main/aiya/rig #

'''
asset = path_info.PathInfo('$RFPROJECT/project/asset/character/main/aiya/model/work')

asset.absPath
# Result: C:/Users/TA/Dropbox/projects/Riff/double_monkey/project_server/project/asset/character/main/aiya/model/work #

asset.relPath
# Result: $RFPROJECT/project/asset/character/main/aiya/model/work #

path_info.convertAbs(asset.relPath)
# Result: C:/Users/TA/Dropbox/projects/Riff/double_monkey/project_server/project/asset/character/main/aiya/model/work #

path_info.convertRel(asset.relPath)
# Result: $RFPROJECT/project/asset/character/main/aiya/model/work #

path_info.convertRoot(str(asset), root='RFPROJECT', absPath=True)
# Result: C:/Users/TA/Dropbox/projects/Riff/double_monkey/project_server/project/asset/character/main/aiya/model/work #

path_info.convertRoot(str(asset), root='RFPROJECT', absPath=False)
# Result: $RFPROJECT/project/asset/character/main/aiya/model/work

'''
