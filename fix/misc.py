import os
import sys 
import maya.cmds as mc 
import maya.mel as mm 

from rftool.utils import path_info
from rftool.fix.polytag import polytag_core
from rftool.utils import maya_utils
reload(maya_utils)
reload(polytag_core)


def quick_export(): 
    sels = mc.ls(sl=True)
    res = 'md'
    geoGrp = 'Geo_Grp'
    rigGrp = 'Rig_Grp'

    for obj in sels: 
        assetName = str()
        libPath = str()

        assetAttr = '%s.assetName' % obj
        libAttr = '%s.path' % obj 

        if mc.objExists(assetAttr): 
            assetName = mc.getAttr(assetAttr)
        if mc.objExists(libAttr): 
            libPath = mc.getAttr(libAttr)

        if assetName and libPath: 
            asset = path_info.PathInfo(path=libPath)
            refPath = asset.libPath()
            rigName = asset.libName(step='rig', res=res, project=False)
            exportPath = '%s/%s' % (refPath, rigName)
            gpuName = os.path.splitext(asset.libName(step='gpu', res=res, project=False, ext='abc'))[0]
            adName = asset.libName('', 'ad', project=False)
            modelName = asset.libName(step='model', res=res, project=False)

            print exportPath
            print refPath, gpuName
            print refPath, modelName

            sgResult = sg_process.create_asset(project=projectEntity, assetType=entitySub1, assetSubType=entitySub2, assetName=entityName, episode=episodeEntity, taskTemplate=taskTemplate)
            if sgResult:
                dirResult = pipeline_utils.create_asset_template(root, projectEntity['name'], entitySub1, entitySub2, entityName)
            # create asset sg 
            # export geo
            # export rig 
            # export gpu 
            # exportResult = maya_utils.export_selection(exportPath, self.rigGrp)
         #    exportGpuResult = maya_utils.export_gpu(geoGrp, refPath, gpuName, time = 'still')
         #    exportGeoResult = maya_utils.export_geo(rigGrp, refPath, modelName)

def list_asset(): 
    from rftool.utils import sg_process
    from rftool.utils import path_info
    res = 'md'
    fields = ['code', 'sg_asset_type', 'sg_subtype']
    sgassets = sg_process.sg.find('Asset', [['project.Project.name', 'is', 'Two_Heroes'], ['sg_asset_type', 'is', 'setDress'], ['sg_subtype', 'is', 'garbage']], fields)

    for i, each in enumerate(sgassets): 
        asset = path_info.PathInfo(project='Two_Heroes', entity='asset', entitySub1=each.get('sg_asset_type'), entitySub2=each.get('sg_subtype'), name=each.get('code'))
        libPath = asset.libPath()
        modelName = asset.libName(step='model', res=res, project=False)
        rigName = asset.libName(step='rig', res=res, project=False)
        
        modelPath = '%s/%s' % (libPath, modelName)
        rigPath = '%s/%s' % (libPath, rigName)
        print '=================='
        print '%s %s' % (i, libPath)

        if os.path.exists(modelPath): 
            try: 
                mc.file(modelPath, o=True, f=True, prompt=False)
            except Exception as e: 
                print e
            clean_file()
            mc.file(rename=modelPath)
            mc.file(save=True, f=True)
        else: 
            print 'missing %s' % modelPath

        if os.path.exists(rigPath): 
            try: 
                mc.file(rigPath, o=True, f=True, prompt=False)
            except Exception as e: 
                print e
            clean_file()
            mc.file(rename=rigPath)
            mc.file(save=True, f=True)
        else: 
            print 'missing %s' % rigPath

        print '========'




def clean_file(): 
    from rftool.utils import maya_utils
    from rftool.utils import pipeline_utils

    # clean plugins 
    maya_utils.remove_plugins()

    # link texture 
    pipeline_utils.relink_texture()

    # auto fill 
    if mc.objExists('Geo_Grp'): 
        childs = mc.listRelatives('Geo_Grp')
        plys = []

        if childs: 
            for child in childs: 
                shape = mc.listRelatives(child, s=True)
                if shape: 
                    if mc.objectType(shape[0], isType='mesh'): 
                        plys.append(child)

        if plys: 
            # mc.select(plys)
            polytag_core.auto_fill2()

    else: 
        if mc.objExists('geo_grp') and mc.objExists('rig_grp'): 
            mc.rename('geo_grp', 'Geo_Grp')
            mc.rename('rig_grp', 'Rig_Grp')
            clean_file()

        else: 
            pass

    if mc.objExists('Rig_Grp'): 
        maya_utils.show_hide_transform(['Rig_Grp'], state=True)


def find_replace(): 
    sels = mc.ls(sl=True)
    grp = 'ok'
    if not mc.objExists(grp): 
        mc.group(em=True, n=grp)

    if sels: 
        for src in sels: 
            assetName = mc.getAttr('%s.assetName' % src)
            srcln = mc.ls(src, l=True)[0]
            mc.select(srcln)
            targets = maya_utils.find_same_poly()

            if targets: 
                targets.remove(src)
                targets.remove(srcln)
                
                for i, target in enumerate(targets): 
                    assetGrp = '%s_Grp' % assetName
                    parent = maya_utils.list_top_parent(target)

                    if not parent == grp: 
                        if not mc.objExists(assetGrp): 
                            mc.group(em=True, n=assetGrp)
                            mc.parent(assetGrp, grp)

                        dup = mc.duplicate(src, n='%s_%02d' % (assetName, i+1))[0]
                        mc.delete(mc.parentConstraint(target, dup))
                        mc.delete(mc.scaleConstraint(target, dup))
                        mc.parent(dup, assetGrp)
                        mc.delete(target)

def find_replace_sels(): 
    sels = mc.ls(sl=True)
    grp = 'ok'
    if not mc.objExists(grp): 
        mc.group(em=True, n=grp)

    if sels: 
        src = sels[0]
        assetName = mc.getAttr('%s.assetName' % src)
        srcln = mc.ls(src, l=True)[0]
        mc.select(srcln)
        targets = sels[1:]

        for i, target in enumerate(targets): 
            assetGrp = '%s_Grp' % assetName
            parent = maya_utils.list_top_parent(target)

            if not parent == grp: 
                if not mc.objExists(assetGrp): 
                    mc.group(em=True, n=assetGrp)
                    mc.parent(assetGrp, grp)

                dup = mc.duplicate(src, n='%s_%02d' % (assetName, i+1))[0]
                mc.delete(mc.parentConstraint(target, dup))
                # mc.delete(mc.scaleConstraint(target, dup))
                mc.parent(dup, assetGrp)
                mc.delete(target)

    
def import_assets(): 
    from rftool.utils import sg_process
    from rftool.utils import path_info
    res = 'md'
    fields = ['code', 'sg_asset_type', 'sg_subtype']
    sgassets = sg_process.sg.find('Asset', [['project.Project.name', 'is', 'Two_Heroes'], ['sg_asset_type', 'is', 'setDress'], ['sg_subtype', 'is', 'garbage']], fields)

    for i, each in enumerate(sgassets): 
        asset = path_info.PathInfo(project='Two_Heroes', entity='asset', entitySub1=each.get('sg_asset_type'), entitySub2=each.get('sg_subtype'), name=each.get('code'))
        libPath = asset.libPath()
        modelName = asset.libName(step='model', res=res, project=False)
        rigName = asset.libName(step='rig', res=res, project=False)
        rigPath = '%s/%s' % (libPath, rigName)

        if os.path.exists(rigPath): 
            mc.file(rigPath, i=True, ns=asset.name)
