import os,subprocess
import maya.cmds as mc
import maya.mel as mm

from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools

from rftool.utils import file_utils
from rftool.utils import maya_utils
from rftool.utils import path_info
from rftool.utils import sg_wrapper
from rftool.utils import ffmpeg_utils


def copy_media_version(prod_dir='',publ_dir='',versionName=''):

    for media in file_utils.listFile(prod_dir):
        if versionName in media:
            prod_path = prod_dir + '/' + media
            publ_path = publ_dir + '/' + media
            print file_utils.copy(prod_path,publ_path)

def copy_asset_hero(entityPath, department, res='md',status='apr'):
    if 'model' == department:
        pub = model_pub(thisScene=entityPath,resolution=res,status='apr')
    else:
        pub = model_pub(thisScene=entityPath,resolution=res,status='apr')

    return pub

def create_asset_pre_publish(entityPath, department, task,status='apr'):
    if 'model' == department:
        pub = model_pub(thisScene=entityPath,taskName=task,status='apr')
    else:
        pub = model_pub(thisScene=entityPath,taskName=task,status='apr')

    return pub

def create_playblast(department, selected = 'all', shotList=None ):

    if selected == 'all':

        for shot in shotList:
            maya_utils.playblast_avi()


def create_increment_work_file(filepath):
    increment_file = file_utils.increment_version(filepath)
    mc.file(rename = increment_file)
    return mc.file(f=True,s=True)

def create_sg_version( project=None, entity=None, versionName=None, task=None, status=None, imagepath='', message='', movie=''):

    prj_ent = sg_wrapper.get_project_entity(project)

    data = {'project': prj_ent, 
            'code': versionName,
            'entity' : entity, 
            'sg_task' : task, 
            'sg_status_list': status } 

    if message:
        data['description'] = message

    if movie:
        data['sg_path_to_movie'] = movie.replace('/','\\')

    ver_ent = sg_wrapper.create_version(data)

    thumbnail = imagepath.replace('####','0001')
    sg_wrapper.upload_thumbnail(ver_ent,thumbnail)

    if movie:
        sg_wrapper.upload_movie(ver_ent,movie)
    
def check_sg_version(version):
    return sg_wrapper.get_version_entity(version)

def set_sg_version(ver_ent,status):

    data = { 'sg_status_list' : status }
    return sg_wrapper.update_version_entity(ver_ent['id'],data)

def set_sg_status(entitys,status):
    data = { 'sg_status_list' : status }

    for entity in entitys:
        result = sg_wrapper.sg.update( entity['type'], entity['id'], data )

class model_pub(object):
    """docstring for model_pub"""
    def __init__(self, thisScene=None, status=None, **kwarg):
        super(model_pub, self).__init__()
        self.thisScene = thisScene

        self.get_info()

        if status == 'rev':
            # self.copy_to_src_publ()
            self.create_hero_res()
            # self.copy_to_lib()
            # self.create_gpu_cache()
            # self.create_abc_cache()

        if status == 'apr':
            self.copy_to_src_publ()
            # self.create_gpu_cache()
            # self.create_abc_cache()
            self.copy_to_lib()

    def get_info(self):
        self.model = path_info.PathInfo(self.thisScene)
        self.asset_name = self.model.name
        self.department = self.model.step
        self.version_name = self.model.versionNoUser
        self.version = file_utils.find_version(self.thisScene)
        self.task_name = self.model.task
        self.resolution = self.task_name.split('_')[-1]

        self.prod_dir = self.model.entityPath(root='RFPROD')
        self.pre_gpu = self.prod_dir  + '/cache/' + '_'.join([self.asset_name,'gpu', self.resolution]) + '.abc'
        self.pre_abc = self.prod_dir  + '/cache/' + '_'.join([self.asset_name,'abc', self.resolution]) + '.abc'
        self.src_publ = self.prod_dir  + '/srcPublish/' + self.version_name + '.ma'

        self.publ_dir = self.model.entityPath(root='RFPUBL') 
        self.publ_path = self.publ_dir + '/publish/' + '_'.join([self.asset_name,self.department,self.resolution,self.version]) + '.ma'

        self.publ_lib = self.publ_dir + '/lib/' + '_'.join([self.asset_name,self.department,self.resolution]) + '.ma'
        self.gpu_lib = self.publ_dir + '/lib/' + '_'.join([self.asset_name,'gpu', self.resolution]) + '.abc'
        self.abc_lib = self.publ_dir + '/lib/' + '_'.join([self.asset_name,'abc', self.resolution]) + '.abc'

        print self.publ_path
        print self.publ_lib

    def copy_to_src_publ(self):
        mc.file(f=True,s=True)
        print file_utils.copy(self.thisScene,self.src_publ)

    def create_hero_res(self):
        if os.path.exists(self.src_publ):

            if not os.path.exists(os.path.dirname(self.publ_path)):
                os.makedirs(os.path.dirname(self.publ_path))

            script_env = os.environ['RFSCRIPT']

            print "C:\\Program Files\\Autodesk\\Maya2016\\bin\\mayapy.exe", "%s\\core\\maya\\rftool\\publish\\utils\\export_utils.py" %(script_env), self.src_publ, self.publ_path, self.department, self.resolution
            subprocess.call(["C:\\Program Files\\Autodesk\\Maya2016\\bin\\mayapy.exe", "%s\\core\\maya\\rftool\\publish\\utils\\export_utils.py" %(script_env), self.src_publ, self.publ_path, self.department, self.resolution])
            # print self.publ_path

    def create_gpu_cache(self):
        if not os.path.exists(os.path.dirname(self.pre_gpu)):
            os.makedirs(os.path.dirname(self.pre_gpu))

        gpu_dir = os.path.dirname(self.pre_gpu)
        gpu_name = os.path.basename(self.pre_gpu).split('.')[0]

        geo_grp = 'Geo_Grp'

        try:
            self.gpu_path = maya_utils.create_gpu_cache(geo_grp,gpu_dir,gpu_name)
        except RuntimeError as exc:
            QtGui.QMessageBox.warning(None, 'Warning', '%s - No objects in the selection can be baked.' %(geo_grp))

    def create_abc_cache(self):
        if not os.path.exists(os.path.dirname(self.pre_abc)):
            os.makedirs(os.path.dirname(self.pre_abc))

        geo_grp = 'Geo_Grp'

        self.abc_path = maya_utils.create_abc_cache(geo_grp, self.pre_abc)

    def copy_to_lib(self):
        if os.path.exists(self.pre_gpu):
            file_utils.copy(self.pre_gpu,self.gpu_lib)
            os.remove(self.pre_gpu)

        if os.path.exists(self.pre_abc):
            file_utils.copy(self.pre_abc,self.abc_lib)
            os.remove(self.pre_abc)

        if os.path.exists(self.publ_path):
            file_utils.copy(self.publ_path,self.publ_lib)

class layout_pub(object):
    """docstring for layout_pub"""
    def __init__(self, thisScene=None, resolution=None):
        super(layout_pub, self).__init__()
        self.thisScene = thisScene
        self.resolution = resolution

        self.get_info()

    def get_info(self):
        self.scene = path_info.PathInfo(self.thisScene)
        self.file_name = self.scene.versionName
        self.user = self.scene.user
        self.version_name = '_'.join(self.scene.fileUser.split('_')[:-1])
        self.version_num = file_utils.find_version(self.thisScene)

        self.prod_dir = self.scene.entityPath(root='RFPROD')
        self.prod_avi = self.prod_dir + '/movies/' + self.version_name + '.avi'
        self.prod_mov = self.prod_dir + '/movies/' + self.version_name + '.mov'
        self.prod_img = self.prod_dir + '/images/' + self.version_name + '.jpg'

    def playblast_all(self):

        shot_chk = []
        movs = []
        imgs = []

        shots = mc.ls(type='shot')
        shots.sort()

        for shot in shots:
            maya_utils.set_first_frame(shot)
            maya_utils.setup_scene_viewport_playblast(shot)
            maya_utils.HUDPlayblast(self.user,self.file_name)

            avi_path = os.path.dirname(self.prod_avi) + '/%s_%s_%s' %(self.version_name.split('_all')[0],shot,self.version_num) + os.path.splitext(self.prod_avi)[-1]
            mov_path = os.path.dirname(self.prod_mov) + '/%s_%s_%s' %(self.version_name.split('_all')[0],shot,self.version_num) + os.path.splitext(self.prod_mov)[-1]
            img_path = os.path.dirname(self.prod_img) + '/%s_%s_%s' %(self.version_name.split('_all')[0],shot,self.version_num) + os.path.splitext(self.prod_img)[-1]
            camName,sf,ef = maya_utils.correct_cam(shot)

            if not ef == 0:
                avi_path = maya_utils.playblast_avi(avi_path,sf,ef,self.resolution)
                mov_path = ffmpeg_utils.convert_to_mov(avi_path,mov_path)
                img_path = maya_utils.playblast_avi(img_path,sf,sf,self.resolution)
                # print avi_path

                movs.append(mov_path)
                imgs.append(img_path)
                shot_chk.append(True)

            else:
                movs.append(None)
                imgs.append(None)
                shot_chk.append(False)

        maya_utils.HUDClear()

        return movs,imgs,shot_chk