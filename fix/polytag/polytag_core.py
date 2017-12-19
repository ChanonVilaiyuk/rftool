# work around for non-reference asset 
# give path and asset infomation tag on ply geometry
import os
import sys 
import maya.cmds as mc 
import maya.mel as mm 
from rftool.utils import maya_utils
from rftool.utils import path_info
from functools import partial 
reload(maya_utils)

def add_multi(): 
    plys = mc.ls(sl=True)

    if plys: 
        for ply in plys: 
            shape = mc.listRelatives(ply, s=True)

            if shape: 
                if mc.objectType(shape[0], isType='mesh'): 
                    add(ply)
                    add_info(ply)

def add(ply): 
    """ add attribute """ 
    add_id(ply)
    add_string(ply, 'project')
    add_string(ply, 'assetName')
    add_string(ply, 'path')
    add_string(ply, 'assetData')

def copy_attr(src, dst): 
    # read 
    id = mc.getAttr('%s.id' % src)
    project = mc.getAttr('%s.project' % src)
    path = mc.getAttr('%s.path' % src)
    assetName = mc.getAttr('%s.assetName' % src)
    assetData = mc.getAttr('%s.assetData' % src)

    # copy 
    mc.setAttr('%s.id' % dst, id)
    mc.setAttr('%s.project' % dst, project, type='string')
    mc.setAttr('%s.assetName' % dst, assetName, type='string')
    mc.setAttr('%s.path' % dst, path, type='string')
    mc.setAttr('%s.assetData' % dst, assetData, type='string')

def add_info(ply): 
    data = {'plyName': ply}
    mc.setAttr('%s.project' % ply, 'Two_Heroes', type='string')
    mc.setAttr('%s.assetData' % ply, str(data), type='string')


def add_string(obj, attr): 
    objAttr = '%s.%s' % (obj, attr)
    if not mc.objExists(objAttr): 
        mc.addAttr(obj, ln=attr, dt='string')
        mc.setAttr('%s.%s' % (obj, attr), e=True, keyable=True)
    return objAttr

def add_id(obj): 
    attr = 'id'
    objAttr = '%s.%s' % (obj, attr)
    if not mc.objExists(objAttr): 
        mc.addAttr(obj, ln=attr, at='long', min=0, dv=0)
        mc.setAttr('%s.%s' % (obj, attr), e=True, keyable=True)
    return objAttr


def transfer_tag(*args): 
    sel = mc.ls(sl=True, l=True)

    if sel: 
        srcObj = sel[0]
        dstObjs = maya_utils.find_same_poly2(srcObj)

        if dstObjs: 
            for dst in dstObjs: 
                if not dst == srcObj: 
                    add(dst)
                    copy_attr(srcObj, dst)

        mc.select(dstObjs)

def transfer_sel_tag(*args): 
    sel = mc.ls(sl=True, l=True)

    if sel: 
        srcObj = sel[0]
        dstObjs = sel[1:]

        if dstObjs: 
            for dst in dstObjs: 
                if not dst == srcObj: 
                    add(dst)
                    copy_attr(srcObj, dst)

        mc.select(dstObjs)


def rename_asset(*args): 
    sel = mc.ls(sl=True, l=True)

    if sel: 
        newObjs = []
        srcObj = sel[0]
        assetName = mc.getAttr('%s.assetName' % srcObj)
        dstObjs = maya_utils.find_same_poly2(srcObj)

        if dstObjs: 
            for i, dst in enumerate(dstObjs): 
                if not dst == srcObj: 
                    newName = '%s_%03d' % (assetName, i)
                    newObj = mc.rename(dst, newName)
                    newObjs.append(newObj)
                else: 
                    mc.rename(dst, assetName)

        mc.select(newObjs)


def auto_fill(*args): 
    from rftool.utils import sg_process
    sels = mc.ls(sl=True)
    caches = dict()
    if sels: 
        for ply in sels: 
            project = mc.getAttr('%s.project' % ply)
            assetName = mc.getAttr('%s.assetName' % ply)
            entity = caches.get(project, {}).get(assetName)

            if not entity: 
                entity = sg_process.sg.find_one('Asset', [['project.Project.name', 'is', project], ['code', 'is', assetName]], ['code', 'sg_asset_type', 'sg_subtype', 'id'])
                print entity
                if entity: 
                    if not project in caches.keys(): 
                        caches.update({project: {assetName: entity}})

            if entity: 
                asset = path_info.PathInfo(project=project, entity='asset', entitySub1=entity.get('sg_asset_type'), entitySub2=entity.get('sg_subtype'), name=assetName)
                libPath = asset.libPath()
                mc.setAttr('%s.id' % ply, entity.get('id'))
                mc.setAttr('%s.path' % ply, libPath, type='string')
                mc.rename(ply, assetName)


def auto_fill2(*args): 
    asset = path_info.PathInfo()
    if mc.objExists('Geo_Grp'): 
        plys = maya_utils.find_ply('Geo_Grp')

        for ply in plys: 
            mc.setAttr('%s.path' % ply, asset.path, type='string')
            mc.setAttr('%s.assetName' % ply, asset.name, type='string')
            mc.setAttr('%s.project' % ply, asset.project, type='string')

        if mc.objExists('Rig_Grp'): 
            add('Rig_Grp')
            copy_attr(plys[0], 'Rig_Grp')


def ui_utils(): 
    def polytag(*args): 
        add_multi()

    def find_same_poly(*args): 
        result = maya_utils.find_same_poly()
        if result: 
            mc.select(result)

    ui = 'polytag_win'
    if mc.window(ui, exists=True): 
        mc.deleteUI(ui)

    win = mc.window(ui)
    mc.columnLayout(adj=1, rs=2)
    mc.button(l='Polytag', h=30, c=polytag)
    mc.button(l='Find same poly', h=30, c=find_same_poly)
    mc.button(l='autofill', h=30, c=auto_fill)
    mc.button(l='transfer tag', h=30, c=transfer_tag)
    mc.button(l='transfer sel tag', h=30, c=transfer_sel_tag)
    mc.button(l='rename asset', h=30, c=rename_asset)
    mc.showWindow()
    mc.window(ui, e=True, wh=[200, 200])


def list_polytag(): 
    meshes = mc.ls(type='mesh')
    info = dict()

    if meshes: 
        meshTransforms = [mc.listRelatives(a, p=True, f=True)[0] for a in meshes if mc.listRelatives(a, p=True)]
        
        for mesh in meshTransforms: 
            projectAttr = '%s.%s' % (mesh, 'project')
            assetAttr = '%s.%s' % (mesh, 'assetName')
            pathAttr = '%s.%s' % (mesh, 'path')

            if mc.objExists(projectAttr) and mc.objExists(assetAttr) and mc.objExists(pathAttr): 
                project = mc.getAttr(projectAttr)
                assetName = mc.getAttr(assetAttr)
                path = mc.getAttr(pathAttr)
                asset = path_info.PathInfo(path=path)

                if not assetName in info.keys(): 
                    info[assetName] = [asset, [mesh]]

                else: 
                    if not mesh in info[assetName][1]: 
                        info[assetName][1].append(mesh)

    return info


def switch_selection(level): 
    sels = mc.ls(sl=True)
    info = dict()
    if sels: 
        for ply in sels: 
            if check_attr(ply): 
                assetName, path, data = get_attr(ply)

                if assetName in info.keys(): 
                    info.get(assetName).append(ply)

                else: 
                    info.update({assetName: [ply]})

    if info: 
        for assetName, plys in info.iteritems(): 
            if len(plys) == 1: 
                switch(plys[0], level)

            if len(plys) > 1: 
                original = None
                for i, ply in enumerate(plys): 
                    if i == 0: 
                        original = switch(ply, level)
                    else: 
                        if original: 
                            switch(ply, level, srcPly=original)
                        else: 
                            switch(ply, level)



def check_attr(ply): 
    # projectAttr = 'project'
    assetNameAttr = '%s.assetName' % ply
    pathAttr = '%s.path' % ply
    dataAttr = '%s.assetData' % ply

    if mc.objExists(assetNameAttr) and mc.objExists(pathAttr) and mc.objExists(dataAttr): 
        return True

def get_attr(ply): 
    assetNameAttr = '%s.assetName' % ply
    pathAttr = '%s.path' % ply
    dataAttr = '%s.assetData' % ply

    assetName = mc.getAttr(assetNameAttr)
    path = mc.getAttr(pathAttr)
    data = mc.getAttr(dataAttr)

    return assetName, path, data

def switch(ply, level, srcPly=None): 
    assetAttr = '%s.%s' % (ply, 'assetName')
    pathAttr = '%s.%s' % (ply, 'path')
    assetDataAttr = '%s.%s' % (ply, 'assetData')
    parent = mc.listRelatives(ply, p=True)

    if mc.objExists(assetAttr) and mc.objExists(pathAttr): 
        assetName = mc.getAttr(assetAttr)
        path = mc.getAttr(pathAttr)
        data = eval(mc.getAttr(assetDataAttr))
        data.update({'original': path})
        asset = path_info.PathInfo(path=path)
        refPath = '%s/%s_%s.ma' % (asset.libPath(), asset.name, level)

        if os.path.exists(refPath): 
            assetPlc = place_asset(refPath, srcPly=srcPly)
            transfer_attr(ply, assetPlc, level)
            
            mc.delete(mc.parentConstraint(ply, assetPlc))
            mc.delete(ply)
            assetPlc = mc.rename(assetPlc, ply)
            mc.parent(assetPlc, parent)

            return assetPlc


def place_asset(refPath, srcPly=None): 
    print 'place asset %s' % refPath
    namespace = 'tmpPlace'
    current = mc.ls(assemblies=True)
    node = ''

    if not mc.namespace(ex=namespace): 
        mc.namespace(add=namespace)
    mc.namespace(set=namespace)
    
    if not srcPly: 
        print 'import'
        mc.file(refPath, i=True)
        placeAssets = [a for a in mc.ls(assemblies=True) if not a in current]
    if srcPly: 
        print 'duplicate'
        placeAssets = mc.duplicate(srcPly)
    mc.namespace(set=':')

    if placeAssets: 
        node = extract_ply(placeAssets)
    
        return node


def extract_ply(placeAssets): 
    print 'import node is %s' % placeAssets
    plys = maya_utils.find_ply(placeAssets[0])
    print 'contains plys %s' % plys

    if plys: 
        if len(plys) > 1: 
            print 'combine'
            cmbPly = mc.polyUnite(plys, mergeUVSets=True, ch=False, n='tmpAsset')
            mc.delete(placeAssets)
            return cmbPly

        if len(plys) == 1: 
            print 'single object'
            mc.parent(plys[0], w=True)

            if not placeAssets[0] == plys[0]: 
                mc.delete(placeAssets)
            return plys[0]

    else: 
        print 'no polygon'
        maya_utils.show_hide_transform(placeAssets, state=True)
        return placeAssets[0]


def transfer_attr(src, dst, level): 
    if not mc.objExists('%s.assetName'): 
        add_string(dst, 'assetName')
        assetName = mc.getAttr('%s.assetName' % src)
        mc.setAttr('%s.assetName' % dst, assetName, type='string')

    if not mc.objExists('%s.path'): 
        add_string(dst, 'path')
        path = mc.getAttr('%s.path' % src)
        mc.setAttr('%s.path' % dst, path, type='string')

    if not mc.objExists('%s.assetData'): 
        add_string(dst, 'assetData')
        assetData = mc.getAttr('%s.assetData' % src)
        mc.setAttr('%s.assetData' % dst, assetData, type='string')
