# standard publish 
import os, sys 
from collections import OrderedDict 
from inspect import getmembers, isfunction
from rftool.utils import path_info
import publish
reload(publish)
import precheck
reload(precheck)
import sg_publish
reload(sg_publish)
import post_publish
reload(post_publish)
from rftool.publish.rf_still_publish import model
reload(model)
from rftool.publish.rf_still_publish import rig
reload(rig)

ui = None

# make order to match the func 
# added function will not be listed if not add to checkOrder below ***

precheckOrder = ['check_naming', 'check_group']
publishOrder = ['publish_file', 'publish_image']
publishWipOrder = ['save_file', 'publish_image']
sg_publishOrder = ['publish_version', 'set_task', 'upload_thumbnail', 'upload_media']

modelOrder = ['export_abc', 'export_gpu']
rigOrder = ['export_abc', 'export_gpu']
postPublishOrder = ['summarized_info']

wipPublishOrder = ['save_file', 'publish_image']

filePublishPreset = {'wip': False, 'rev': False, 'arpv': True}
overridePublishPreset = {'wip': [precheckOrder, wipPublishOrder, sg_publishOrder, postPublishOrder], 
						'filePublish': [precheckOrder, publishOrder, sg_publishOrder, postPublishOrder]}

def load_publish_list(pathInfo, preset): 
	# 
	# preset functions 
	if preset in overridePublishPreset.keys(): 
		precheckOrderFilter, publishOrderFilter, sg_publishOrderFilter, postPublishOrderFilter = overridePublishPreset[preset]

	deptPubl = []
	standardPubls = set_order([a for a in getmembers(publish) if isfunction(a[1])], publishOrderFilter)
	precheckList = set_order([a for a in getmembers(precheck) if isfunction(a[1])], precheckOrderFilter)
	sgPubls = set_order([a for a in getmembers(sg_publish) if isfunction(a[1])], sg_publishOrderFilter)
	postPubls = set_order([a for a in getmembers(post_publish) if isfunction(a[1])], postPublishOrderFilter)
	funcDict = OrderedDict()

	if pathInfo.path: 
		if pathInfo.step == 'model': 
			deptPubl = set_order([a for a in getmembers(model) if isfunction(a[1])], modelOrder)
			dept = model 

		if pathInfo.step == 'rig': 
			deptPubl = set_order([a for a in getmembers(model) if isfunction(a[1])], rigOrder)
			dept = model 


		# disable department publish if preset is work in progresss
		if preset == 'wip': 
			deptPubl = []

		funcDict['publ'] = (publish, standardPubls)
		funcDict['precheckList'] = (precheck, precheckList)
		funcDict['sgPubls'] = (sg_publish, sgPubls)
		funcDict['deptPubl'] = (dept, deptPubl)
		funcDict['postPubl'] = (post_publish, postPubls)

	return funcDict 


def set_order(funcs, order): 
	tempDict = dict()
	orderList = []

	for name, func in funcs: 
		tempDict[name] = func 

	for func in order: 
		if func in tempDict.keys(): 
			orderList.append((func, tempDict[func]))
	return orderList


def publish_version(source): 
	entity = path_info.PathInfo(source)
	version = entity.versionNoUser
	return version


def linenumber_of_member(m):
    try:
        return m[1].im_func.func_code.co_firstlineno
    except AttributeError:
        return -1

