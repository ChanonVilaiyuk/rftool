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
from rftool.publish.rf_still_publish import model
reload(model)

ui = None

def load_publish_list(pathInfo): 
	# 
	deptPubl = []
	standardPubls = [a for a in getmembers(publish) if isfunction(a[1])]
	precheckList = [a for a in getmembers(precheck) if isfunction(a[1])]
	sgPubls = [a for a in getmembers(sg_publish) if isfunction(a[1])]
	funcDict = OrderedDict()

	if pathInfo.path: 
		if pathInfo.step == 'model': 
			deptPubl = [a for a in getmembers(model) if isfunction(a[1])]
			dept = model 

		funcDict['publ'] = (publish, standardPubls)
		funcDict['deptPubl'] = (dept, deptPubl)
		funcDict['precheckList'] = (precheck, precheckList)
		funcDict['sgPubls'] = (sg_publish, sgPubls)

	return funcDict 

def publish_version(source): 
	entity = path_info.PathInfo(source)
	version = entity.versionNoUser
	return version


def linenumber_of_member(m):
    try:
        return m[1].im_func.func_code.co_firstlineno
    except AttributeError:
        return -1

