import os
import maya.cmds as mc
import maya.mel as mm

import asm_utils

for path in os.environ['MAYA_PLUG_IN_PATH'].split(';'):
    if os.path.exists(path + '/AbcImport.mll'):
        if not mc.pluginInfo('AbcImport.mll', q=True, l=True):
            mc.loadPlugin(path + '/AbcImport.mll')

    if os.path.exists(path + '/AbcExport.mll'):
        if not mc.pluginInfo('AbcExport.mll', q=True, l=True):
            mc.loadPlugin(path + '/AbcExport.mll')

    if os.path.exists(path + '/gpuCache.mll'):
        if not mc.pluginInfo('gpuCache.mll', q=True, l=True):
            mc.loadPlugin(path + '/gpuCache.mll')

def get_path():
    return mc.file(q=True, loc=True)

def setup_asset_viewport_capture():
    mc.grid(toggle=0)
    perspPanel = mc.getPanel( withLabel='Persp View')
    mc.modelEditor(perspPanel,e=True,hud=False)
    mc.setAttr("defaultResolution.width",1024)
    mc.setAttr("defaultResolution.height",1024)

def setup_scene_viewport_playblast():
    mc.grid(toggle=0)
    perspPanel = mc.getPanel( withLabel='Persp View')
    mc.modelEditor(perspPanel,e=True,hud=False)
    mc.setAttr("defaultResolution.width",1024)
    mc.setAttr("defaultResolution.height",1024)

def playblast_capture_1k(image_path, atFrame=None):
    file_extention = image_path.split('.')[-1]
    index = int(image_path.split('.')[-2])
    image_no_extention = image_path.split('.')[0]
    print image_no_extention

    if not atFrame:
        atFrame = index

    result = mc.playblast(format='image',
                    filename=image_no_extention,
                    st=atFrame,
                    et=atFrame,
                    sequenceTime=0,
                    clearCache=1,
                    viewer=0,
                    showOrnaments=1,
                    fp=4,
                    percent=100,
                    compression=file_extention,
                    quality=100,
                    widthHeight=[1024,1024])

    if result:
        print 'result', result
        # result = result.replace('####',image_path.split('.')[-2])
        targetFile = result.replace('####',image_path.split('.')[-2]).replace('\\', '/')
        tmpFile = result.replace('####',atFrame).replace('\\', '/')
        print atFrame
        print tmpFile
        print targetFile

        if os.path.exists(tmpFile):
            os.rename(tmpFile, targetFile)

        print 'result', result

        return targetFile

def playblast_avi(mov_path,start,end,resolution,width=960,height=540):
    # playblast  -fmt "avi" -startTime 301 -endTime 325 -sequenceTime 1 -forceOverwrite -filename "movies/s0030.avi" -clearCache 1 -showOrnaments 0 -percent 100 -wh 1024 778 -offScreen -viewer 0 -useTraxSounds -compression "none" -quality 70;
    image_no_extention = mov_path.split('.')[0]
    file_extention = mov_path.split('.')[-1]

    if file_extention == 'avi':
        result = mc.playblast(format=file_extention,
                        filename=mov_path,
                        st=start,
                        et=end,
                        sequenceTime=1,
                        forceOverwrite=True,
                        clearCache=1,
                        viewer=0,
                        showOrnaments=1,
                        percent=100,
                        compression="none",
                        quality=resolution,
                        widthHeight=[width,height],
                        useTraxSounds=True)

    if file_extention == 'jpg':
        result = mc.playblast(format='image',
                    filename=image_no_extention,
                    st=start,
                    et=start,
                    sequenceTime=0,
                    clearCache=1,
                    viewer=0,
                    showOrnaments=1,
                    fp=4,
                    percent=100,
                    compression=file_extention,
                    quality=100,
                    widthHeight=[width,height])
        result = result.replace('####','%04d' %(start))

    return result

def correct_cam(shotName):
    cam_name = shotName + '_cam'
    st = 0
    et = 0

    if mc.shot(shotName, q=True ,currentCamera=True) == cam_name:
        st = mc.getAttr('%s.startFrame' %(shotName))
        et = mc.getAttr('%s.endFrame' %(shotName))

    return cam_name,st,et

def setup_scene_viewport_playblast(shotName):
    mc.grid(toggle=0)

    mc.setAttr("defaultResolution.width",960)
    mc.setAttr("defaultResolution.height",540)

    if mc.objExists(shotName):
        mc.setAttr('%s_camShape.displayGateMask' %(shotName), True)
        mc.setAttr('%s_camShape.displayResolution' %(shotName), True)
        mc.setAttr('%s_camShape.displayGateMaskOpacity' %(shotName), 1)
        mc.setAttr('%s_camShape.displayGateMaskColor' %(shotName), 0, 0, 0, type='double3')
        mc.setAttr('%s_camShape.overscan' %(shotName),1.0)

def get_current_shot():
    return mc.sequenceManager(q=True,currentShot=True)

def get_current_frame_no(shotName):
    cam_name, sf, ef = correct_cam(shotName)
    ft = (ef - sf) + 1.0
    cf = mc.currentTime(q=True)
    ct = (cf - sf) + 1.0

    return '%d/%d' %(ct,ft)

def get_current_frame(shotName):
    cam_name, sf, ef = correct_cam(shotName)
    cf = mc.currentTime(q=True)

    return '%d/%d' %(cf,ef)

def set_first_frame(shotName):
    st = mc.getAttr('%s.startFrame' %(shotName))
    mc.currentTime(st)
    mc.sequenceManager(currentTime=st)


def HUDClear():
    for hud in mc.headsUpDisplay(listHeadsUpDisplays=True):
        mc.headsUpDisplay(hud,edit=True, visible=False)
        mc.headsUpDisplay(hud,refresh=True)

def HUDPlayblast(user,versionName):

    HUDClear()

    hud_lists = [ 'HUDUsername', 'HUDCurrentTime', 'HUDFilename', 'HUDCurrentShot', 'HUDCurrentFrame', 'HUDOverAll' ]

    # [i for i, j in zip(a, b) if i == j]

    # Left-Bottom
    mc.headsUpDisplay( rp=(5, 3) )
    if not mc.headsUpDisplay('HUDUsername', exists=True):
        mc.headsUpDisplay('HUDUsername', section=5, block=3, label='User : ', command='sp_app.path_info.PathInfo().user', attachToRefresh=True, blockAlignment='left')
    if mc.headsUpDisplay('HUDUsername',exists = True):
        mc.headsUpDisplay('HUDUsername', edit=True, section=5, block=3, label='User : ', command='sp_app.path_info.PathInfo().user', attachToRefresh=True, blockAlignment='left')
    mc.headsUpDisplay( rp=(5, 2) )
    if not mc.headsUpDisplay('HUDCurrentTime',exists = True):
        mc.headsUpDisplay('HUDCurrentTime', section=5, block=2, label='Date/Time : ', command='sp_app.file_utils.get_now_time()', attachToRefresh=True, blockAlignment='left')
    if mc.headsUpDisplay('HUDCurrentTime',exists = True):
        mc.headsUpDisplay('HUDCurrentTime', edit=True, section=5, block=2, label='Date/Time : ', command='sp_app.file_utils.get_now_time()', attachToRefresh=True, blockAlignment='left')
    mc.headsUpDisplay( rp=(5, 1) )
    if not mc.headsUpDisplay('HUDFilename',exists = True):
        mc.headsUpDisplay('HUDFilename', section=5, block=1, label='Filename : ', command='sp_app.path_info.PathInfo().versionName', attachToRefresh=True, blockAlignment='left')
    if mc.headsUpDisplay('HUDFilename',exists = True):
        mc.headsUpDisplay('HUDFilename', edit=True, section=5, block=1, label='Filename : ', command='sp_app.path_info.PathInfo().versionName', attachToRefresh=True, blockAlignment='left')

    # Center-Bottom
    mc.headsUpDisplay( rp=(7, 2) )
    if not mc.headsUpDisplay('HUDCurrentShot',exists = True):
        mc.headsUpDisplay('HUDCurrentShot', section=7, block=2, label='Cam : ', command='sp_app.maya_utils.get_current_shot()', attachToRefresh=True, blockAlignment='center', dataFontSize='large')
    if mc.headsUpDisplay('HUDCurrentShot',exists = True):
        mc.headsUpDisplay('HUDCurrentShot', edit=True, section=7, block=2, label='Cam : ', command='sp_app.maya_utils.get_current_shot()', attachToRefresh=True, blockAlignment='center', dataFontSize='large')
    mc.headsUpDisplay( rp=(7, 1) )
    if not mc.headsUpDisplay('HUDCurrentFrame',exists = True):
        mc.headsUpDisplay('HUDCurrentFrame', section=7, block=1, label='Info : ', command='sp_app.maya_utils.get_current_frame_no(sp_app.maya_utils.get_current_shot())', attachToRefresh=True, blockAlignment='center', dataFontSize='large')
    if mc.headsUpDisplay('HUDCurrentFrame',exists = True):
        mc.headsUpDisplay('HUDCurrentFrame', edit=True, section=7, block=1, label='Info : ', command='sp_app.maya_utils.get_current_frame_no(sp_app.maya_utils.get_current_shot())', attachToRefresh=True, blockAlignment='center', dataFontSize='large')

    # Right-Bottom
    mc.headsUpDisplay( rp=(9, 2) )
    if mc.headsUpDisplay('HUDFocalLength',exists = True):
        mc.headsUpDisplay('HUDFocalLength', edit=True, section=9, block=2, attachToRefresh=True, blockAlignment='right')
    mc.headsUpDisplay( rp=(9, 1) )
    if not mc.headsUpDisplay('HUDOverAll',exists = True):
        mc.headsUpDisplay('HUDOverAll', section=9, block=1, label='Over all : ', command='sp_app.maya_utils.get_current_frame(sp_app.maya_utils.get_current_shot())', attachToRefresh=True, blockAlignment='right', dataFontSize='large')
    if mc.headsUpDisplay('HUDOverAll',exists = True):
        mc.headsUpDisplay('HUDOverAll', edit=True, section=9, block=1, label='Over all : ', command='sp_app.maya_utils.get_current_frame(sp_app.maya_utils.get_current_shot())', attachToRefresh=True, blockAlignment='right', dataFontSize='large')


# def create_rig_grp(res='md', ctrl=False):
#     plys = mc.ls(sl=True,l=True)

#     if not mc.objExists('Geo_Grp'):
#         geo_grp = mc.group(em=True,name='Geo_Grp')
#         still_grp = mc.group(em=True,name='Still_Grp')
#         offset_grp = mc.group(em=True,name='Offset_Grp')
#         rig_grp = mc.group(em=True,name='Rig_Grp')

#         if ctrl:
#             ctrl_grp = mc.group(em=True,name='Ctrl_Grp')
#             mc.parent(ctrl_grp,rig_grp)
#             ctrl_grp = mc.group(em=True,name='Placement_Ctrl')

#         mc.parent(geo_grp,rig_grp)
#         mc.parent(still_grp,rig_grp)
#         mc.parent(offset_grp,rig_grp)

#         md_geo_grp = mc.group(em=True,name='Md_Geo_Grp')
#         mc.parent(md_geo_grp,geo_grp)
#         hi_geo_grp = mc.group(em=True,name='Hi_Geo_Grp')
#         mc.parent(hi_geo_grp,geo_grp)
#         lo_geo_grp = mc.group(em=True,name='Lo_Geo_Grp')
#         mc.parent(lo_geo_grp,geo_grp)

#     if plys:
#         if res == 'md':
#             mc.parent(plys, 'Md_Geo_Grp')
#         if res == 'lo':
#             mc.parent(plys, 'Lo_Geo_Grp')
#         if res == 'hi':
#             mc.parent(plys, 'Hi_Geo_Grp')

#     for ply in plys:
#         oldname = ply.split('|')[-1]
#         newname = '_'.join([res,oldname])
#         mc.rename(oldname,newname)

def create_rig_grp(objs=None, res='md', ctrl=True):
    from rftool.rig.utils import main_group
    if not objs:
        objs = mc.ls(sl=True)

    rigGrp = main_group.MainGroup('rig')

    if not ctrl:
        mc.delete(rigGrp.Place_Ctrl)

    if objs:
        if res == 'md':
            mc.parent(objs, rigGrp.Geo_Md)
        if res == 'hi':
            mc.parent(objs, rigGrp.Geo_Hi)
        if res == 'lo':
            mc.parent(objs, rigGrp.Geo_Lo)
        if res == 'pr':
            mc.parent(objs, rigGrp.Geo_Pr)

    return rigGrp


def create_gpu_cache(objName='',gpuDirname='',gpuBasename=''):
    # gpuCache -startTime 1 -endTime 1 -optimize -optimizationThreshold 40000 -writeMaterials -dataFormat ogawa -directory "C:/Users/vanef/Dropbox/media_server/project/asset/prop/general/glass/prePublish" -fileName "glass_gpu" Md_Geo_Grp;
    return mc.gpuCache(objName,startTime=1,endTime=1,optimize=True,optimizationThreshold=40000,writeMaterials=True,dataFormat="ogawa",fileName=gpuBasename,directory=gpuDirname)

def create_abc_cache(objLongName='',abcPath=''):
    # AbcExport -j "-frameRange 1 1 -uvWrite -worldSpace -writeVisibility -dataFormat ogawa -root |Rig_Grp|Geo_Grp|Md_Geo_Grp -file C:/Users/vanef/Dropbox/media_server/project/asset/prop/general/glass/cache/glass_abc.abc";
    return mc.AbcExport(j="-frameRange 1 1 -uvWrite -worldSpace -writeVisibility -dataFormat ogawa -root %s -file %s" %(objLongName,abcPath))

def check_duplicate_name():

    if mc.objExists('rig_grp'):
        mc.select('rig_grp', hi=True )
        lists = mc.ls(sl=True,type='transform')

        mc.select(clear=True)
        unDup = []

        for list in lists:
            #print list.split('|')[-1]
            if not list.split('|')[-1] in unDup:
                unDup.append(list.split('|')[-1])

            else:
                mc.select(('*%s*') %(list.split('|')[-1]), add=True)

        if mc.ls(sl=True):
            return False

        else:
            return True

# def HUDPlayblast():
#     from rftool.utils import path_info
#     path = path_info.PathInfo()
#     filename = path.versionName

#     mc.headsUpDisplay('HUDFilename', section=1, block=5, label='Filename : ', command='path.versionName')
#     mc.headsUpDisplay('HUDFilename', edit=True, visability=True)

def create_reference(assetName, path):
    if os.path.exists(path):
        namespace = get_namespace('%s_001' % assetName)
        result = mc.file(path, r=True, ns=namespace)
        return namespace

def create_asm_reference(assetName, path):
    if os.path.exists(path):
        namespace = get_namespace('%s_001' % assetName)
        arNode = asm_utils.createARNode()
        asm_utils.setARDefinitionPath(arNode, path)
        # asm_utils.setARNamespace(arNode, namespace)
        mc.rename(arNode, '%s_AR' % assetName)

        return namespace

def duplicate_reference(path):
    namespace = mc.file(path, q=True, namespace=True)
    newNamespace = get_namespace(namespace)
    result = mc.file(path, r=True, ns=newNamespace)
    return newNamespace

def get_namespace(namespace):
    # asset_001
    if not mc.namespace(ex=namespace):
        return namespace

    else:
        padding = namespace.split('_')[-1]
        if padding.isdigit():
            incrementPadding = '%03d' % (int(padding) + 1)
            newNamespace = namespace.replace(padding, incrementPadding)

        else:
            newNamespace = '%s_001' % namespace

        return get_namespace(newNamespace)
