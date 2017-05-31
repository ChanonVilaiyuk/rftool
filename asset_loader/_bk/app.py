import os,sys,shutil
sys.path.append('O:/script_server/core/maya/lib')
sys.path.append('O:/script_server/core/maya/rftool')
sys.path.append('O:/script_server/config')
sys.path.append('O:/script_server/python/2.7/site-packages')

module_path = sys.modules[__name__].__file__
module_dir = os.path.dirname(module_path)

import config

# import PySide
# from PyQt4 import sip
# from sip import PyQt4
# from PyQt4 import QtCore
# from PyQt4 import QtGui
# from PyQt4 import uic

from shotgun_api3 import Shotgun
from utils import url_utils

server = config.server
script = config.script
id = config.id
sg = Shotgun(server, script, id)

project_name = 'Shotgun_Test'
shot_name = 'Shot010'

sg_asset_types = []
sg_asset_subtypes = []
sg_asset_names = []

lists_asset_types = []
lists_asset_subtypes = []
lists_asset_names = []

def sg_get_project():
    return sg.find('Project',filters=[],fields=['name'])

def sg_get_asset(project_name):
    filters = [['project.Project.name','is',project_name]]
    return sg.find('Asset',filters,fields=['code','sg_asset_type','sg_subtype','image'])

def get_project():
    sg_project = dict()

    for i in sg_wrapper.get_projects():
        project_name = i['name']
        sg_project[project_name] = i

    return sg_project

def list_sorted(lists, asset_check=True):

    none_check = False

    if lists:
        if None in lists:
            lists.remove(None)
            none_check = True

        lists = sorted(lists, key=str.lower)

        if none_check :
            lists.insert(0, '(Blank)')

        if asset_check :
            lists.insert(0, 'All')

    return lists

def sg_asset_lists():
    sg_assets = sg_get_asset(project_name)
    sg_asset_types = []
    sg_asset_subtypes = []
    sg_asset_names = []

    for i in sg_assets:
        if not i['sg_asset_type'] in sg_asset_types:
            sg_asset_types.append(i['sg_asset_type'])
        if not i['sg_subtype'] in sg_asset_subtypes:
            sg_asset_subtypes.append(i['sg_subtype'])
        if not i['code'] in sg_asset_names:
            sg_asset_names.append(i['code'])

    lists_asset_types     = list_sorted(sg_asset_types)
    lists_asset_subtypes  = list_sorted(sg_asset_subtypes)
    lists_asset_names     = list_sorted(sg_asset_names,False)

def selected_list(type_name='All',subtype_name='All',asset_name='All'):

    lists_asset_subtypes = []
    lists_asset_names = []

    for i in sg_assets:

        if (type_name == i['sg_asset_type']) or (type_name == '(Blank)' and i['sg_asset_type'] == None):
            
            if not i['sg_subtype'] in lists_asset_subtypes:
                lists_asset_subtypes.append(i['sg_subtype'])

            if subtype_name == i['sg_subtype']:
                lists_asset_names.append(i['code'])

            if subtype_name == 'All':
                lists_asset_names.append(i['code'])

        if type_name == 'All':
            lists_asset_subtypes.append(i['sg_subtype'])
            lists_asset_names.append(i['code'])

    lists_asset_subtypes = list_sorted(lists_asset_subtypes)
    lists_asset_names = list_sorted(lists_asset_names,False)
    # print lists_asset_subtypes
    # print lists_asset_names

def sg_get_entitys_thumbnail(entitys):
    # entity with ['image','code'] fields.
    tmp_icon = 'O:/script_server/icon/tmp_thumbnail.jpg'
    
    for i in entitys:

        icon_dir = 'O:/script_server/icon/_sg/thumbnail'
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)

        icon_path = icon_dir + '/' + i['code'] + '.jpg'

        if not i['image'] == None:
            url_utils.download_from_url(i['image'],icon_path)
        else:
            shutil.copy(tmp_icon,icon_path)

        i['image'] = icon_path
        print '- Download thumbnail : ' + icon_path

    return entitys

# def sg_get_shot():

asset_entitys = sg_get_asset(project_name)

filters = [ ['project.Project.name', 'is', project_name],
            ['code', 'is', shot_name] ]

shot_entity = sg.find_one('Shot',filters,fields=[])


def sg_set_assets_to_shot(asset_entitys, shot_entity):

    shot_id = shot_entity['id']
    data = { 'assets' : asset_entitys }

    return sg.update('Shot',shot_id,data)

print sg_set_assets_to_shot(asset_entitys, shot_entity)


# # first SG Lists
# sg_asset_lists()
# # respond with listWidgetItem selected
# selected_list(type_name='Prop',subtype_name='primitives')

# # get thumbnail from shotgun
# sg_assets = sg_get_asset(project_name)
# sg_assets = sg_get_assets_thumbnail(sg_assets)
