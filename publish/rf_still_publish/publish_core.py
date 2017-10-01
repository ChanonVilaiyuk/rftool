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

import config
reload(config)

def load_publish_list(pathInfo, preset): 
	# 
	# preset functions 
	if preset in config.overridePublishPreset.keys(): 
		precheckOrderFilter, publishOrderFilter, sg_publishOrderFilter, postPublishOrderFilter = config.overridePublishPreset[preset]

	deptPubl = []
	dept = None
	standardPubls = set_order([a for a in getmembers(publish) if isfunction(a[1])], publishOrderFilter)
	precheckList = set_order([a for a in getmembers(precheck) if isfunction(a[1])], precheckOrderFilter)
	sgPubls = set_order([a for a in getmembers(sg_publish) if isfunction(a[1])], sg_publishOrderFilter)
	postPubls = set_order([a for a in getmembers(post_publish) if isfunction(a[1])], postPublishOrderFilter)
	funcDict = OrderedDict()

	if pathInfo.path: 
		if pathInfo.step == 'model': 
			deptPubl = set_order([a for a in getmembers(model) if isfunction(a[1])], config.modelOrder)
			dept = model 

		if pathInfo.step == 'rig': 
			deptPubl = set_order([a for a in getmembers(rig) if isfunction(a[1])], config.rigOrder)
			dept = rig 


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

