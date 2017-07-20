# v.0.0.1
# layout split UI file

# v.0.0.1 basic ui working

#Import python modules
import sys, os, re, subprocess, inspect
import platform
import getpass
moduleDir = os.path.dirname(sys.modules[__name__].__file__)

#Import maya commands
try:
    import maya.cmds as mc
    import maya.mel as mm
    import maya.OpenMayaUI as mui

    isMaya = True

except ImportError:
    isMaya = False
    packagePath = '%s/python/2.7/site-packages' % os.environ['RFSCRIPT']
    toolPath = '%s/core/maya' % os.environ['RFSCRIPT']
    corePath = '%s/core' % os.environ['RFSCRIPT']
    qtPath = '%s/lib/Qt.py' % os.environ['RFSCRIPT']
    appendPaths = [packagePath, toolPath, corePath, qtPath]

    # add PySide lib path
    for path in appendPaths:
        if not path in sys.path:
            sys.path.append(path)

    from startup import setEnv
    reload(setEnv)
    setEnv.set()

from rftool.utils import log_utils
from rftool.utils import maya_utils
from rftool.utils import pipeline_utils
from rftool.utils import path_info
from rftool.utils import sg_process
from startup import config
import maya_hook as hook
reload(hook)

reload(maya_utils)
reload(config)

logFile = log_utils.name('split_shot_layout', user=getpass.getuser())
logger = log_utils.init_logger(logFile)


def shiftShot(shotName):
    """ split only shotName """
    # assume that startFrame and sequenceStartFrame are the same
    startFrame = mc.getAttr('%s.startFrame' % shotName)
    endFrame = mc.getAttr('%s.endFrame' % shotName)
    duration = endFrame - startFrame + 1
    shiftFrameCount = config.shotStartFrame - startFrame

    if not shiftFrameCount == 0:
        maya_utils.shiftKey(frame=shiftFrameCount)
        logger.info('Shift key %s frames success' % shiftFrameCount)

        maya_utils.shiftSequencer(frame=shiftFrameCount, mute=True)
        logger.info('Shift sequencer %s frames success' % shiftFrameCount)
        mc.shot(shotName, e=True, mute=False)

        endRange = config.shotStartFrame + duration - 1
        mc.playbackOptions(min=config.shotStartFrame, max=endRange)
        mc.playbackOptions(ast=config.shotStartFrame, aet=endRange)
        logger.info('Set range to %s-%s' % (config.shotStartFrame, endRange))

def split_shots(scenePath=None, shots=None, saveTmp=True, shotgun=True):
    sequenceShots = mc.ls(type='shot')
    if not shots:
        shots = sequenceShots

    # current scene
    sequence = path_info.PathInfo()
    if scenePath:
        sequence = path_info.PathInfo(scenePath)

    if sequence.path:
        sequencePath = sequence.entity2Path()

        if saveTmp:
            hook.saveTmpFile(sequence)

        # shotgun
        if shotgun:
            sequenceEntity = sg_process.get_one_sequence(sequence.project, sequence.episode, sequence.sequenceName(project=True), fields=['project', 'sg_episode'])
            projectEntity = sequenceEntity.get('project', dict())
            episodeEntity = sequenceEntity.get('sg_episode', dict())

        executeShots = []
        for shotName in shots:
            if shotName in sequenceShots:
                logger.info('start on shot %s ===================\n' % shotName)
                step = 'anim'
                shot = path_info.PathInfo(project=sequence.project, entity=config.scene, entitySub1=sequence.episode, entitySub2=sequence.sequence, name=shotName, step=step)

                # create shot structure
                pipeline_utils.create_scene_template(config.RFPROJECT, shot.project, shot.episode, shot.sequence, shotName)
                logger.info('Create shot directory for %s complete' % shotName)

                if shotgun:
                    shotCode = '%s_%s' % (shot.sequenceName(project=True), shotName)
                    sg_process.create_shot(projectEntity, episodeEntity, sequenceEntity, shotCode, shotName, template='default')
                    logger.info('Create shotgun shot for %s complete' % shotCode)

                #shift shot
                shiftShot(shotName)

                # save file
                result = hook.saveSplitFile(shot)
                logger.info('shot %s complete ===================\n' % shotName)
                executeShots.append(shotName)

            else:
                logger.warning('Input shot not exists %s' % shotName)
                logger.warning('Existing shots are %s' % sequenceShots)

        logger.info('-------------------------------------')
        logger.info('Split %s shots complete' % (len(executeShots)))

    else:
        logger.warning('Scene not in the pipeline')
