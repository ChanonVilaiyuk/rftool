import sys 
import os 
import maya.cmds as mc 
import maya.mel as mm 

def findSamePoly(sel = True) : 
	# find similar polygon by count faces
	sels = mc.ls(sl = True)

	if sels : 
		numFace = mc.polyEvaluate(sels[0], f = True, fmt = True)

		matchPoly = []
		matchPoly.append(sels[0])

		mc.select(cl = True)
		allPlys = mc.ls(type = 'mesh', l = True)

		for each in allPlys : 
			transform = mc.listRelatives(each, p = True, f = True)[0]
			currentFaceCount = mc.polyEvaluate(each, f = True, fmt = True)
			
			if currentFaceCount == numFace : 
				matchPoly.append(transform)
				
		if sel : 
			mc.select(matchPoly)

		return matchPoly


def findSamePoly2(obj) : 
	# find similar polygon by count faces

	numFace = mc.polyEvaluate(obj, f = True, fmt = True)

	matchPoly = []
	matchPoly.append(obj)

	mc.select(cl = True)
	allPlys = mc.ls(type = 'mesh', l = True)

	for each in allPlys : 
		transform = mc.listRelatives(each, p = True, f = True)[0]
		currentFaceCount = mc.polyEvaluate(each, f = True, fmt = True)
		
		if currentFaceCount == numFace : 
			if not transform in matchPoly : 
				matchPoly.append(transform)

	return matchPoly


def import_cache(): 
	pass 

def import_lookdev(): 
	pass 

