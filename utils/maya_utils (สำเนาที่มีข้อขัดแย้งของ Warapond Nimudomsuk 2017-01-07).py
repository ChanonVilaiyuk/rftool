import os
import maya.cmds as mc
import maya.mel as mm

for path in os.environ['MAYA_PLUG_IN_PATH'].split(';'):
    if os.path.exists(path + '/AbcImport.mll'):
        mc.loadPlugin(path + '/AbcImport.mll')

    if os.path.exists(path + '/AbcExport.mll'):
        mc.loadPlugin(path + '/AbcExport.mll')

    if os.path.exists(path + '/gpuCache.mll'):
        mc.loadPlugin(path + '/gpuCache.mll')

def get_path():
    return mc.file(q=True, loc=True)

def setup_asset_viewport_capture():
    mc.grid(toggle=0)
    perspPanel = mc.getPanel( withLabel='Persp View')
    mc.modelEditor(perspPanel,e=True,hud=False)
    mc.setAttr("defaultResolution.width",1024)
    mc.setAttr("defaultResolution.height",1024)

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
        mc.headsUpDisplay('HUDUsername', section=5, block=3, label='User : ', command='sp_app.path_info.PathInfo().user', event='timeChanged', blockAlignment='left', visible=True)
    if mc.headsUpDisplay('HUDUsername',exists = True):
        mc.headsUpDisplay('HUDUsername', edit=True, section=5, block=3, label='User : ', command='sp_app.path_info.PathInfo().user', event='timeChanged', blockAlignment='left', visible=True)
    mc.headsUpDisplay( rp=(5, 2) )
    if not mc.headsUpDisplay('HUDCurrentTime',exists = True):
        mc.headsUpDisplay('HUDCurrentTime', section=5, block=2, label='Date/Time : ', command='sp_app.file_utils.get_now_time()', event='timeChanged', blockAlignment='left', visible=True)
    if mc.headsUpDisplay('HUDCurrentTime',exists = True):
        mc.headsUpDisplay('HUDCurrentTime', edit=True, section=5, block=2, label='Date/Time : ', command='sp_app.file_utils.get_now_time()', event='timeChanged', blockAlignment='left', visible=True)
    mc.headsUpDisplay( rp=(5, 1) )
    if not mc.headsUpDisplay('HUDFilename',exists = True):
        mc.headsUpDisplay('HUDFilename', section=5, block=1, label='Filename : ', command='sp_app.path_info.PathInfo().versionName', event='timeChanged', blockAlignment='left', visible=True)
    if mc.headsUpDisplay('HUDFilename',exists = True):
        mc.headsUpDisplay('HUDFilename', edit=True, section=5, block=1, label='Filename : ', command='sp_app.path_info.PathInfo().versionName', event='timeChanged', blockAlignment='left', visible=True)

    # Center-Bottom
    mc.headsUpDisplay( rp=(7, 2) )
    if not mc.headsUpDisplay('HUDCurrentShot',exists = True):
        mc.headsUpDisplay('HUDCurrentShot', section=7, block=2, label='Cam : ', command='sp_app.maya_utils.get_current_shot()', event='timeChanged', blockAlignment='center', dataFontSize='large', visible=True)
    if mc.headsUpDisplay('HUDCurrentShot',exists = True):
        mc.headsUpDisplay('HUDCurrentShot', edit=True, section=7, block=2, label='Cam : ', command='sp_app.maya_utils.get_current_shot()', event='timeChanged', blockAlignment='center', dataFontSize='large', visible=True)
    mc.headsUpDisplay( rp=(7, 1) )
    if not mc.headsUpDisplay('HUDCurrentFrame',exists = True):
        mc.headsUpDisplay('HUDCurrentFrame', section=7, block=1, label='Info : ', command='sp_app.maya_utils.get_current_frame_no(sp_app.maya_utils.get_current_shot())', event='timeChanged', blockAlignment='center', dataFontSize='large', visible=True)
    if mc.headsUpDisplay('HUDCurrentFrame',exists = True):
        mc.headsUpDisplay('HUDCurrentFrame', edit=True, section=7, block=1, label='Info : ', command='sp_app.maya_utils.get_current_frame_no(sp_app.maya_utils.get_current_shot())', event='timeChanged', blockAlignment='center', dataFontSize='large', visible=True)

    # Right-Bottom
    mc.headsUpDisplay( rp=(9, 2) )
    if mc.headsUpDisplay('HUDFocalLength',exists = True):
        mc.headsUpDisplay('HUDFocalLength', edit=True, section=9, block=2, event='timeChanged', blockAlignment='right', visible=True)
    mc.headsUpDisplay( rp=(9, 1) )
    if not mc.headsUpDisplay('HUDOverAll',exists = True):
        mc.headsUpDisplay('HUDOverAll', section=9, block=1, label='Over all : ', command='sp_app.maya_utils.get_current_frame(sp_app.maya_utils.get_current_shot())', event='timeChanged', blockAlignment='right', dataFontSize='large', visible=True)
    if mc.headsUpDisplay('HUDOverAll',exists = True):
        mc.headsUpDisplay('HUDOverAll', edit=True, section=9, block=1, label='Over all : ', command='sp_app.maya_utils.get_current_frame(sp_app.maya_utils.get_current_shot())', event='timeChanged', blockAlignment='right', dataFontSize='large', visible=True)


def playblast_capture_1k(image_path):
    file_extention = image_path.split('.')[-1]
    index = int(image_path.split('.')[-2])
    image_no_extention = image_path.split('.')[0]

    result = mc.playblast(format='image',
                    filename=image_no_extention,
                    st=index,
                    et=index,
                    sequenceTime=0,
                    clearCache=1,
                    viewer=0,
                    showOrnaments=0,
                    fp=4,
                    percent=100,
                    compression=file_extention,
                    quality=100,
                    widthHeight=[1024,1024])

    if result:
        result = result.replace('####',image_path.split('.')[-2])

    return result

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
                    showOrnaments=0,
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
        mc.currentTime(st)

    return cam_name,st,et

def create_rig_grp(res='md'):
    plys = mc.ls(sl=True,l=True)

    if plys:
        if not mc.objExists('Geo_Grp'):
            geo_grp = mc.group(em=True,name='Geo_Grp')
            still_grp = mc.group(em=True,name='Still_Grp')
            offset_grp = mc.group(em=True,name='Offset_Grp')
            rig_grp = mc.group(em=True,name='Rig_Grp')

            mc.parent(geo_grp,rig_grp)
            mc.parent(still_grp,rig_grp)
            mc.parent(offset_grp,rig_grp)

            md_geo_grp = mc.group(em=True,name='Md_Geo_Grp')
            mc.parent(md_geo_grp,geo_grp)
            hi_geo_grp = mc.group(em=True,name='Hi_Geo_Grp')
            mc.parent(hi_geo_grp,geo_grp)
            lo_geo_grp = mc.group(em=True,name='Lo_Geo_Grp')
            mc.parent(lo_geo_grp,geo_grp)

        if res == 'md':
            mc.parent(plys, 'Md_Geo_Grp')
        if res == 'lo':
            mc.parent(plys, 'Lo_Geo_Grp')
        if res == 'hi':
            mc.parent(plys, 'Hi_Geo_Grp')

        for ply in plys:
            oldname = ply.split('|')[-1]
            newname = '_'.join([res,oldname])
            mc.rename(oldname,newname)

def create_gpu_cache(objName='',gpuDirname='',gpuBasename=''):
    # gpuCache -startTime 1 -endTime 1 -optimize -optimizationThreshold 40000 -writeMaterials -dataFormat ogawa -directory "C:/Users/vanef/Dropbox/media_server/project/asset/prop/general/glass/prePublish" -fileName "glass_gpu" Md_Geo_Grp;
    return mc.gpuCache(objName,startTime=1,endTime=1,optimize=True,optimizationThreshold=40000,writeMaterials=True,dataFormat="ogawa",fileName=gpuBasename,directory=gpuDirname)

def create_abc_cache(objLongName='',abcPath=''):
    # AbcExport -j "-frameRange 1 1 -uvWrite -worldSpace -writeVisibility -dataFormat ogawa -root |Rig_Grp|Geo_Grp|Md_Geo_Grp -file C:/Users/vanef/Dropbox/media_server/project/asset/prop/general/glass/cache/glass_abc.abc";
    return mc.AbcExport(j="-frameRange 1 1 -uvWrite -worldSpace -writeVisibility -dataFormat ogawa -root %s -file %s" %(objLongName,abcPath))

def check_duplicate_name():
    
    if mc.objExists('Rig_Grp'):
        mc.select('Rig_Grp', hi=True )
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

