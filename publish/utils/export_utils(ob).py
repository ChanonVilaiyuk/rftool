
import sys,os
import maya.standalone
import maya.cmds as mc
import maya.mel as mm
maya.standalone.initialize()
# import pymel
# module_path  = sys.modules[__name__].__file__
# module_split = module_path.split('\\')
# module_dir = '\\'.join(module_split[:-4])
# sys.path.append(module_dir)

def exprot_core():
    src_path = sys.argv[1]
    dst_path = sys.argv[2]
    department = sys.argv[3]
    resolution = sys.argv[4]

	if department == 'model':
		export_model(src_path,dst_path,resolution)
	else:
		export_model(src_path,dst_path,resolution)
	
def export_model(src_path,dst_path,res='md'):
	
    geo_grps = ['Md_Geo_Grp', 'Hi_Geo_Grp','Lo_Geo_Grp'] 

    if res == 'lo':
        geo_grp = 'Lo_Geo_Grp'
    if res == 'md':
        geo_grp = 'Md_Geo_Grp'
    if res == 'hi':
        geo_grp = 'Hi_Geo_Grp'

    geo_grps.remove(geo_grp)

    mc.file(src_path,f=True,o=True,typ="mayaAscii",options="v=0")

    for grp in geo_grps:
    	if mc.objExists(grp):
    		mc.delete(grp)

    mc.file(rename=dst_path)
    mc.file(save=True,f=True,typ="mayaAscii",options="v=0")

exprot_core()