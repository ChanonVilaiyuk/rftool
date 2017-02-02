import os
import re
import math

import maya.cmds as mc
import maya.mel as mm

def addGimbal(obj=''):

	'''
	Adding gimbal helper to the given node.
	'''

	ctrl = Dag(obj)
	ctrlShape = Dag(ctrl.shape)
	
	tmpCtrl = mc.duplicate(ctrl, rr=True)[0]
	
	ctrlShape.add(ln='gimbalControl', min=0, max=1, k=True)
	
	gmblCtrl = Null()
	parentShape(tmpCtrl, gmblCtrl)
	gmblCtrlShape = Dag(gmblCtrl.shape)
	gmblCtrlShape.name = '%sShape' % gmblCtrl.name
	gmblCtrl.color = 'white'
	gmblCtrl.snap(ctrl)
	gmblCtrl.parent(ctrl)
	
	ctrlShape.attr('gimbalControl') >> gmblCtrlShape.attr('v')
	
	attrs = ('sx', 'sy', 'sz', 'v')
	for attr in attrs:
		gmblCtrl.attr(attr).lockHide()
	
	return gmblCtrl

def addConCtrl(obj=''):
	'''
	Adding a controller, for constraining, above the given node.
	Basically, this controller is for contraining purpose.
	'''
	ctrl = Dag(obj)
	ctrlShape = Dag(ctrl.shape)
	
	tmpCtrl = mc.duplicate(ctrl, rr=True)[0]
	
	ctrlShape.add(ln='conControl', min=0, max=1, k=True)
	
	conCtrl = Null()
	parentShape(tmpCtrl, conCtrl)
	conCtrlShape = Dag(conCtrl.shape)
	conCtrlShape.name = '%sShape' % conCtrl.name
	conCtrl.color = 'softBlue'
	
	# Parenting and positioning
	parent = ctrl.getParent()
	conCtrl.snap(parent)
	conCtrl.parent(parent)
	ctrl.parent(conCtrl)
	
	ctrlShape.attr('conControl') >> conCtrlShape.attr('v')
	
	attrs = ('sx', 'sy', 'sz', 'v')
	for attr in attrs:
		conCtrl.attr(attr).lockHide()
	
	return conCtrl

def parentShape(source = '', target = ''):
	
	src = Dag(source)
	trgt = Dag(target)
	
	mc.parent(src.shape, trgt, s = True, r = True)
	mc.delete(src)

def arclen(*args, **kwargs):
	cif = mc.arclen(*args, **kwargs)
	return Node(cif)

def circle(*args, **kwargs):
	return Dag(mc.circle(*args, **kwargs)[0])

def curve(*args, **kwargs):
	return Dag(mc.curve(*args, **kwargs))

def duplicateCurve(*args, **kwargs):
	tmp = mc.duplicateCurve(*args, **kwargs)
	crv = Dag(tmp[0])
	cfs = Node(tmp[1])
	return crv, cfs

def nurbsPlane(*args, **kwargs):
	return Dag(mc.nurbsPlane(*args, **kwargs)[0])

def group(*args, **kwargs):
	grp = Dag(mc.group(*args, **kwargs))
	grp.attr('rp').value = (0,0,0)
	grp.attr('sp').value = (0,0,0)
	return grp

def listAllChildren(obj = ''):
	return mc.listRelatives(obj, ad = True, type = 'transform')

def parentConstraint(*args, **kwargs):
	# parentConstraint command
	return Constraint(mc.parentConstraint(*args, **kwargs)[0])

def pointConstraint(*args, **kwargs):
	# pointConstraint command
	return Constraint(mc.pointConstraint(*args, **kwargs)[0])

def orientConstraint(*args, **kwargs):
	# orientConstraint command
	return Constraint(mc.orientConstraint(*args, **kwargs)[0])

def aimConstraint(*args, **kwargs):
	# aimConstraint command
	return Constraint(mc.aimConstraint(*args, **kwargs)[0])

def scaleConstraint(*args, **kwargs):
	# scaleConstraint command
	return Constraint(mc.scaleConstraint(*args, **kwargs)[0])

def poleVectorConstraint(*args, **kwargs):
	# poleVectorConstraint command
	return Constraint(mc.poleVectorConstraint(*args, **kwargs)[0])

def tangentConstraint(*args, **kwargs):
	# tangentConstraint command
	return Constraint(mc.tangentConstraint(*args, **kwargs)[0])

# Math tools
def pos(obj):
	return mc.xform(obj, q=True, t=True, ws=True)

def diff(a, b):
	return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]

def dot(a, b):
	return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def cross(a, b):
	c = [a[1]*b[2] - a[2]*b[1],
		 a[2]*b[0] - a[0]*b[2],
		 a[0]*b[1] - a[1]*b[0]]

	return c

def mag(vct=(0, 0, 0)):
	return pow(pow(vct[0],2) + pow(vct[1],2) + pow(vct[2],2), 0.5)

def norm(vct=(0, 0, 0)):
	return [ix/mag(vct) for ix in vct]

def angle(a, b):
	return math.acos(dot(a, b) / (mag(a) * mag(b)))

def distance(a='', b=''):
	
	objA = Dag(a)
	objB = Dag(b)
			
	return mag(diff(objB.ws, objA.ws))

def matMult(a=[], b=[]):
	'''
	Multiply two matrices
	a = [
			[a0, a1, a2, a3],
			[a4, a5, a6, a7],
			[a8, a9, a10, a11],
			[a12, a13, a14, a15]
		]
	b = [
			[b0, b1, b2, b3],
			[b4, b5, b6, b7],
			[b8, b9, b10, b11],
			[b12, b13, b14, b15]
		]
	'''
	return [[sum(a*b for a, b in zip(aRow, bCol)) for bCol in zip(*b)] for aRow in a]

def toMat(m=[]):
	'''
	Convert list of numbers to square matrix.
	a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
	result = [
				[1, 2, 3,],
				[4, 5, 6],
				[7, 8, 9]
			]
	'''
	range_ = range(int(pow(len(m), 0.5)))
	result = []
	
	ix = 0
	for iy in range_:
		col = []
		for iz in range_:
			col.append(m[ix])
			ix += 1
		result.append(col)

	return result

class Attribute(object):
	# Template class for Attributes in this module
	def __init__(self, attrName = ''):
		self.name = str(attrName)
	
	def __str__(self):
		return str(self.name)
	
	def __repr__(self):
		return str(self.name)
	
	def __floordiv__(self, attr = ''):
		mc.disconnectAttr(self, attr)
	
	def __rshift__(self, target = ''):
		try:
			mc.connectAttr(self, target, f = True)
		except RuntimeError:
			print '%s has already connected to %s' % (self, target)

	# v/value property
	def getVal(self):
		
		val = mc.getAttr(self)
		
		if type(val) is type([]) or type(val) is type(()):
			return val[0]
		else:
			return val
	
	def setVal(self, val):
		if type(val) == type(()) or type(val) == type([]):
			node, attr = self.name.split('.')
			chldrn = mc.attributeQuery(attr, node = node, lc = True)
			
			for ix in range(0, len(chldrn)):
				mc.setAttr('%s.%s' % (node, chldrn[ix]), val[ix])
		else:
			mc.setAttr(self, val)
	
	value = property(getVal, setVal, None, None)
	v = property(getVal, setVal, None, None)

	# cb/channelBox property
	def getCb(self):
		return mc.getAttr(self, cb = True)
	
	def setCb(self, val = False):
		mc.setAttr(self, cb = val)
	
	channelBox = property(getCb, setCb, None, None)
	cb = property(getCb, setCb, None, None)
	
	# l/lock property
	def getLock(self):
		return mc.getAttr(self, l = True)
	
	def setLock(self, val = False):
		mc.setAttr(self, l = val)
	
	lock = property(getLock, setLock, None, None)
	l = property(getLock, setLock, None, None)
	
	# h/hide property
	def getHide(self):
		return not mc.getAttr(self, k = True)
	
	def setHide(self, val = False):
		mc.setAttr(self, k = not val)
		mc.setAttr(self, cb = not val)
	
	hide = property(getHide, setHide, None, None)
	h = property(getHide, setHide, None, None)
	
	# Lock and hide attribute
	def lockHide(self):
		mc.setAttr(self, l=True)
		mc.setAttr(self, k=False)
	
	def set(self, *args, **kwargs):
		
		mc.setAttr(self, *args, **kwargs)
	
	# Exists property
	def getExists(self):
		return mc.objExists(self)
	
	exists = property(getExists, None, None, None)

class Node(object):
	# Template class for maya nodes in this module
	def __init__(self, name):
		self.__name = str(name)
		mc.select(cl = True)
	
	# def __del__(self):
		# mc.delete(self)
	
	def __str__(self):
		return str(self.name)
	
	def __repr__(self):
		return str(self.name)
	
	# Name properties
	def getName(self):
		return self.__name
	
	def rename(self, newName):
		self.__name = str(mc.rename(self.__name, newName))
	
	name = property(getName, rename, None, None)
	
	# Type property
	def getType(self):
		return mc.nodeType(self.name)
	
	type = property(getType, None, None, None)
	
	# Exists property
	def getExists(self):
		return mc.objExists(self)
	
	exists = property(getExists, None, None, None)
	
	# Attribute tools
	def attr(self, attrName = ''):
		return Attribute('%s.%s' % (self, attrName))
		
	def add(self, *args, **kwargs):
		mc.addAttr(self, *args, **kwargs)
		
	def lockHideAttrs(self, *args):
		for arg in args:
			if arg in ('t', 'r', 's'):
				for ax in ('x', 'y', 'z'):
					mc.setAttr('%s.%s%s' % (self, arg, ax), l = True, k = False)
			else:
				mc.setAttr('%s.%s' % (self, arg), l = True, k = False)
		
	def lockAttrs(self, *args):
		for arg in args:
			if arg in ('t', 'r', 's'):
				for ax in ('x', 'y', 'z'):
					mc.setAttr('%s.%s%s' % (self, arg, ax), l = True)
			else:
				mc.setAttr('%s.%s' % (self, arg), l = True)
		
	def lockHideKeyableAttrs(self):
		# Lock and hide keyable attributes
		attrs = mc.listAttr(self.name, k = True)
		
		for attr in attrs:
			# Do nothing if attribute is multi
			if mc.attributeQuery(attr.split('.')[0], n = self.name, multi = True):
				continue
			else:
				mc.setAttr('%s.%s' % (self.name, attr), l = True, k = False)
	
	def lockKeyableAttrs(self):
		# Lock and hide keyable attributes
		attrs = mc.listAttr(self.name, k = True)
		
		for attr in attrs:
			# Do nothing if attribute is multi
			if mc.attributeQuery(attr.split('.')[0], n = self.name, multi = True):
				continue
			else:
				mc.setAttr('%s.%s' % (self.name, attr), l = True)

class RemapValue(Node):
	# remapValue object
	def __init__(self):
		Node.__init__(self, mc.createNode('remapValue'))

class PointOnCurveInfo(Node):
	# pointOnCurveInfo object
	def __init__(self):
		Node.__init__(self, mc.createNode('pointOnCurveInfo'))

class NearestPointOnCurve(Node):
	# nearestPointOnCurve object
	def __init__(self):
		Node.__init__(self, mc.createNode('nearestPointOnCurve'))

class ClosestPointOnSurface(Node):
	# closestPointOnSurface object
	def __init__(self):
		Node.__init__(self, mc.createNode('closestPointOnSurface'))

class PointOnSurfaceInfo(Node):
	# pointOnSurface object
	def __init__(self):
		Node.__init__(self, mc.createNode('pointOnSurfaceInfo'))

class CurveInfo(Node):
	# pointOnCurve object
	def __init__(self):
		Node.__init__(self, mc.createNode('curveInfo'))

class AddDoubleLinear(Node):
	# addDoubleLinear object
	def __init__(self):
		Node.__init__(self, mc.createNode('addDoubleLinear'))

class Condition(Node):
	# condition object
	def __init__(self):
		Node.__init__(self, mc.createNode('condition'))

class MultDoubleLinear(Node):
	# multDoubleLinear object
	def __init__(self):
		Node.__init__(self, mc.createNode('multDoubleLinear'))

class PlusMinusAverageTemplate(Node):
	
	# Template class for plusMinusAverage object
	
	def __init__(self, name=''):
		Node.__init__(self, name)
	
	def last1D(self):
		# Find the first connectable input1D attribute
		sources = mc.listConnections('%s.input1D' % self.name, d = False, s = True, p = True)
		if sources:
			for ix in range(len(sources) + 1):
				if not mc.listConnections('%s.input1D[%s]' % (self.name, str(ix)), d = False, s = True, p = True):
					return Attribute('%s.input1D[%s]' % (self.name, str(ix)))
		else:
			return Attribute('%s.input1D[0]' % self.name)

	def last3D(self):
		# Find the first connectable input3D attribute
		sources = mc.listConnections('%s.input3D' % self.name, d = False, s = True, p = True)
		if sources:
			for ix in range(len(sources) + 1):
				if not mc.listConnections('%s.input3D[%s]' % (self.name, str(ix)), d = False, s = True, p = True):
					return Attribute('%s.input3D[%s]' % (self.name, str(ix)))
		else:
			return Attribute('%s.input3D[0]' % self.name)

class PlusMinusAverage(PlusMinusAverageTemplate):
	# plusMinusAverage object
	def __init__(self):
		PlusMinusAverageTemplate.__init__(self, mc.createNode('plusMinusAverage'))
	
class MultiplyDivide(Node):
	# multiplyDivide object
	def __init__(self):
		Node.__init__(self, mc.createNode('multiplyDivide'))

class BlendColors(Node):
	# blendColors object
	def __init__(self):
		Node.__init__(self, mc.createNode('blendColors'))

class BlendTwoAttr(Node):
	# blendTwoAttr object
	def __init__(self):
		Node.__init__(self, mc.createNode('blendTwoAttr'))
	
	def last(self):
		# Find connectable input1D attribute
		sources = mc.listConnections('%s.input' % self.name, d = False, s = True, p = True)
		if sources:
			for ix in range(len(sources) + 1):
				if not mc.listConnections('%s.input[%s]' % (self.name, str(ix)), d = False, s = True, p = True):
					return '%s.input[%s]' % (self.name, str(ix))
		else:
			return Attribute('%s.input[0]' % self.name)
	
class DistanceBetween(Node):
	# distanceBetween object
	def __init__(self):
		Node.__init__(self, mc.createNode('distanceBetween'))

class AngleBetween(Node):
	# angleBetween object
	def __init__(self):
		Node.__init__(self, mc.createNode('angleBetween'))

class Reverse(Node):
	# reverse object
	def __init__(self):
		Node.__init__(self, mc.createNode('reverse'))

class CurveFromMeshEdge(Node):
	# curveFromMeshEdge object
	def __init__(self):
		Node.__init__(self, mc.createNode('curveFromMeshEdge'))

class Loft(Node):
	# loft object
	def __init__(self):
		Node.__init__(self, mc.createNode('loft'))

class Clamp(Node):
	# clamp object
	def __init__(self):
		Node.__init__(self, mc.createNode('clamp'))

class SkinCluster(Node):
	# skinCluster object
	def __init__(self, *args, **kwargs):
		
		Node.__init__(self, mc.skinCluster(*args, **kwargs)[0])

class Dag(Node):
	# Template class for DAG nodes in this module
	def __init__(self, nodeName = ''):
		Node.__init__(self, nodeName)
	
	# shape properties
	def getShape(self):
		shapes = mc.listRelatives(self.name, shapes = True)
		if shapes:
			if len(shapes) > 1:
				return shapes[0]
			else:
				return shapes[0]
	
	def renameShape(self, newName):
		shapes = mc.listRelatives(self.name, shapes = True)
		if shapes:
			for shape in shapes:
				mc.rename(shape, newName)
	
	shape = property(getShape, None, None, None)
	
	# color property
	def getColor(self):
		return mc.getAttr('%s.overrideColor' % self.shape)
	
	def setColor(self, cin):
		
		obj = self.shape
		
		cDic = {
				'black': 1,
				'gray': 2,
				'softGray': 3,
				'darkBlue': 15,
				'blue': 6,
				'darkGreen': 7,
				'brown': 11,
				'darkRed': 12,
				'red': 13,
				'green': 14,
				'white': 16,
				'yellow': 17,
				'softYellow': 21,
				'softBlue': 18,
				'softRed': 31
				}
		
		if type(cin) == type(str()):
			if cin in cDic.keys():
				cid = cDic[cin]
			else:
				cid = 0
		else:
			cid = cin
		
		if type(obj) is type([]):
			
			mc.setAttr('%s.overrideEnabled' % obj[0], 1)
			mc.setAttr('%s.overrideColor' % obj[0], cid)
		else:
			
			mc.setAttr('%s.overrideEnabled' % obj, 1)
			mc.setAttr('%s.overrideColor' % obj, cid)
	
	color = property(getColor, setColor, None, None)
	
	# rotate order property
	def getRotateOrder(self):
		roDct = {
				'xyz': 0,
				'yzx': 1,
				'zxy': 2,
				'xzy': 3,
				'yxz': 4,
				'zyx': 5
				}
		roId = mc.getAttr('%s.rotateOrder' % self.name)
		
		for key in roDct.keys():
			if roId == roDct[key]:
				return roId

	def setRotateOrder(self, ro):
		roDct = {
				'xyz': 0,
				'yzx': 1,
				'zxy': 2,
				'xzy': 3,
				'yxz': 4,
				'zyx': 5
				}
		
		if ro in roDct.keys():
			val = roDct[ro]
		else:
			val = ro
		
		mc.setAttr('%s.rotateOrder' % self.name, val)
	
	rotateOrder = property(getRotateOrder, setRotateOrder, None, None)
	
	# World space property
	def getWs(self):
		
		validTypes = ('transform','joint')
		
		if self.type in validTypes:
			pos = mc.xform(self, q = True, ws = True, t = True)
			return (float(pos[0]),float(pos[1]),float(pos[2]))
	
	ws = property(getWs, None, None, None)
	
	# Transform tools
	def getParent(self):
		# Get parent node
		obj = mc.listRelatives(self, p = True)
		
		if obj:
			return Dag(obj[0])
		else:
			return None
		
	def parent(self, target = '', **kwargs):
		if target:
			mc.parent(self, target, **kwargs)
		else:
			mc.parent(self, w = True, **kwargs)
		mc.select(cl = True)
	
	def freeze(self, **kwargs):
		mc.makeIdentity(self, a=True, **kwargs)
	
	def snap(self, target):
		# Match current position and orientation to target
		mc.delete(mc.parentConstraint(target, self.name, mo=False))
	
	def snapPoint(self, target):
		# Match current position to target
		mc.delete(mc.pointConstraint(target, self.name, mo=False))
	
	def snapOrient(self, target):
		# Match current orientation to target
		mc.delete(mc.orientConstraint(target, self.name, mo=False))
	
	def snapScale(self, target):
		# Match current scale to target
		mc.delete(mc.scaleConstraint(target, self.name, mo=False))

	# Curve tools
	def curveParameter(self, curveType):
		# Returns parameter by specific curve type.
		# The valid types are
		# 'crossArrow', 'plus', 'circle', 'cube', 'capsule', 'stick' and 'sphere'
		if curveType == 'crossArrow':
			parameter = [(0,0,-2.192969), (0.851882,0,-1.266891), (0.511129,0,-1.266891),
				(0.511129,0,-0.633446), (0.633446,0,-0.511129), (1.266891,0,-0.511129),
				(1.266891,0,-0.851882), (2.192969,0,0), (1.266891,0,0.851882), (1.266891,0,0.511129),
				(0.633446,0,0.511129), (0.511129,0,0.633446), (0.511129,0,1.266891), (0.851882,0,1.266891),
				(0,0,2.192969), (-0.851882,0,1.266891), (-0.511129,0,1.266891), (-0.511129,0,0.633446),
				(-0.633446,0,0.511129), (-1.266891,0,0.511129), (-1.266891,0,0.851882), (-2.192969,0,0),
				(-1.266891,0,-0.851882), (-1.266891,0,-0.511129), (-0.633446,0,-0.511129),
				(-0.511129,0,-0.633446), (-0.511129,0,-1.266891), (-0.851882,0,-1.266891), (0,0,-2.192969)]
		
		elif curveType == 'plus':
			parameter = [(0,1,0), (0,-1,0), (0,0,0), (-1,0,0), (1,0,0), (0,0,0), (0,0,-1), (0,0,1)]
		
		elif curveType == 'circle':
			parameter = [(1.125,0,0), (1.004121,0,0), (0.991758,0,-0.157079), (0.954976,0,-0.31029),
				(0.894678,0,-0.455861), (0.812351,0,-0.590207), (0.710021,0,-0.710021),
				(0.590207,0,-0.812351), (0.455861,0,-0.894678), (0.31029,0,-0.954976),
				(0.157079,0,-0.991758), (0,0,-1.004121), (0,0,-1.125), (0,0,-1.004121),
				(-0.157079,0,-0.991758), (-0.31029,0,-0.954976), (-0.455861,0,-0.894678),
				(-0.590207,0,-0.812351), (-0.710021,0,-0.710021), (-0.812351,0,-0.590207),
				(-0.894678,0,-0.455861), (-0.954976,0,-0.31029), (-0.991758,0,-0.157079),
				(-1.004121,0,0), (-1.125,0,0), (-1.004121,0,0), (-0.991758,0,0.157079),
				(-0.954976,0,0.31029), (-0.894678,0,0.455861), (-0.812351,0,0.590207),
				(-0.710021,0,0.710021), (-0.590207,0,0.812351), (-0.455861,0,0.894678),
				(-0.31029,0,0.954976), (-0.157079,0,0.991758), (0,0,1.004121), (0,0,1.125),
				(0,0,1.004121), (0.157079,0,0.991758), (0.31029,0,0.954976), (0.455861,0,0.894678),
				(0.590207,0,0.812351), (0.710021,0,0.710021), (0.812351,0,0.590207), (0.894678,0,0.455861),
				(0.954976,0,0.31029), (0.991758,0,0.157079), (1.004121,0,0)]
		
		elif curveType == 'cube':
			parameter = [(-1, 0, -1), (-1, 0, 1), (-1, 2, 1), (-1, 0, 1), (1, 0, 1), (1, 2, 1),
			(1, 0, 1), (1, 0, -1), (1, 2, -1), (1, 0, -1), (-1, 0, -1), (-1, 2, -1), (1, 2, -1),
			(1, 2, 1), (-1, 2, 1), (-1, 2, -1)]
		
		elif curveType == 'capsule':
			parameter = [(-2.011489,0,0), (-1.977023,0.261792,0), (-1.875975,0.505744,0),
			(-1.71523,0.71523,0), (-1.505744,0.875975,0), (-1.261792,0.977023,0), (-1,1.011489,0),
			(1,1.011489,0), (1.261792,0.977023,0), (1.505744,0.875975,0), (1.71523,0.71523,0),
			(1.875975,0.505744,0), (1.977023,0.261792,0), (2.011489,0,0), (1.977023,-0.261792,0),
			(1.875975,-0.505744,0), (1.71523,-0.71523,0), (1.505744,-0.875975,0), (1.261792,-0.977023,0),
			(1,-1.011489,0), (-1,-1.011489,0), (-1.261792,-0.977023,0), (-1.505744,-0.875975,0),
			(-1.71523,-0.71523,0), (-1.875975,-0.505744,0), (-1.977023,-0.261792,0), (-2.011489,0,0)]
		
		elif curveType == 'stick':
			parameter = [(0,0,0), (0,1.499085,0), (0.0523598,1.501829,0), (0.104146,1.510032,0),
			(0.154791,1.523602,0), (0.20374,1.542392,0), (0.250457,1.566195,0), (0.29443,1.594752,0),
			(0.335177,1.627748,0), (0.372252,1.664823,0), (0.405248,1.70557,0), (0.433805,1.749543,0),
			(0.457608,1.79626,0), (0.476398,1.845209,0), (0.489968,1.895854,0), (0.498171,1.94764,0),
			(0.500915,2,0), (0.498171,2.05236,0), (0.489968,2.104146,0), (0.476398,2.154791,0),
			(0.457608,2.20374,0), (0.433805,2.250457,0), (0.405248,2.29443,0), (0.372252,2.335177,0),
			(0.335177,2.372252,0), (0.29443,2.405248,0), (0.250457,2.433805,0), (0.20374,2.457608,0),
			(0.154791,2.476398,0), (0.104146,2.489968,0), (0.0523598,2.498171,0), (0,2.500915,0),
			(-0.0523598,2.498171,0), (-0.104146,2.489968,0), (-0.154791,2.476398,0), (-0.20374,2.457608,0),
			(-0.250457,2.433805,0), (-0.29443,2.405248,0), (-0.335177,2.372252,0), (-0.372252,2.335177,0),
			(-0.405248,2.29443,0), (-0.433805,2.250457,0), (-0.457608,2.20374,0), (-0.476398,2.154791,0),
			(-0.489968,2.104146,0), (-0.498171,2.05236,0), (-0.500915,2,0), (-0.498171,1.94764,0),
			(-0.489968,1.895854,0), (-0.476398,1.845209,0), (-0.457608,1.79626,0), (-0.433805,1.749543,0),
			(-0.405248,1.70557,0), (-0.372252,1.664823,0), (-0.335177,1.627748,0), (-0.29443,1.594752,0),
			(-0.250457,1.566195,0), (-0.20374,1.542392,0), (-0.154791,1.523602,0), (-0.104146,1.510032,0),
			(-0.0523598,1.501829,0), (0,1.499085,0)]
		
		elif curveType == 'sphere':
			parameter = [(-1.5,0,0), (-1,0,0), (-0.965926,0.258819,0), (-0.866026,0.5,0),
			(-0.707107,0.707107,0), (-0.5,0.866025,0), (-0.258819,0.965926,0), (0,1,0), (0,1.5,0), (0,1,0),
			(0.258819,0.965926,0), (0.5,0.866025,0), (0.707107,0.707107,0), (0.866025,0.5,0),
			(0.965926,0.258819,0), (1,0,0), (1.5,0,0), (1,0,0), (0.965926,-0.258819,0), (0.866025,-0.5,0),
			(0.707107,-0.707107,0), (0.5,-0.866025,0), (0.258819,-0.965926,0), (0,-1,0), (0,-1.5,0),
			(0,-1,0), (-0.258819,-0.965926,0), (-0.5,-0.866025,0), (-0.707107,-0.707107,0),
			(-0.866026,-0.5,0), (-0.965926,-0.258819,0), (-1,0,0), (-0.951057,0,0.309017),
			(-0.809017,0,0.587785), (-0.587785,0,0.809017), (-0.309017,0,0.951057), (-2.98023e-08,0,1),
			(0,0,1.5), (-2.98023e-08,0,1), (0.309017,0,0.951057), (0.587785,0,0.809017),
			(0.809017,0,0.587785), (0.951057,0,0.309017), (1,0,0), (0.951057,0,-0.309017),
			(0.809018,0,-0.587786), (0.587786,0,-0.809017), (0.309017,0,-0.951057), (0,0,-1),
			(0,0,-1.5), (0,0,-1), (0,0.258819,-0.965926), (0,0.5,-0.866026), (0,0.707107,-0.707107),
			(0,0.866025,-0.5), (0,0.965926,-0.258819), (0,1,0), (-7.71341e-09,0.965926,0.258819),
			(-1.49012e-08,0.866025,0.5), (-2.10734e-08,0.707107,0.707107), (-2.58096e-08,0.5,0.866026),
			(-2.87868e-08,0.258819,0.965926), (-2.98023e-08,0,1), (-2.87868e-08,-0.258819,0.965926),
			(-2.58096e-08,-0.5,0.866026), (-2.10734e-08,-0.707107,0.707107), (-1.49012e-08,-0.866025,0.5),
			(-7.71341e-09,-0.965926,0.258819), (0,-1,0), (0,-0.965926,-0.258819), (0,-0.866025,-0.5),
			(0,-0.707107,-0.707107), (0,-0.5,-0.866026), (0,-0.258819,-0.965926), (0,0,-1),
			(-0.309017,0,-0.951057), (-0.587785,0,-0.809017), (-0.809017,0,-0.587785),
			(-0.951057,0,-0.309017), (-1,0,0)]
		
		elif curveType == 'square':
			parameter = [(-1, 0, 0), (-1, 2, 0), (1, 2, 0), (1, 0, 0), (-1, 0, 0)]
		
		elif curveType == 'doubleStick':
			parameter = [(0,-1.499085,0), (-0.0523598,-1.501829,0), (-0.104146,-1.510032,0),
			(-0.154791,-1.523602,0), (-0.20374,-1.542392,0), (-0.250457,-1.566195,0),
			(-0.29443,-1.594752,0), (-0.335177,-1.627748,0), (-0.372252,-1.664823,0),
			(-0.405248,-1.70557,0), (-0.433805,-1.749543,0), (-0.457608,-1.79626,0),
			(-0.476398,-1.845209,0), (-0.489968,-1.895854,0), (-0.498171,-1.94764,0),
			(-0.500915,-2,0), (-0.498171,-2.05236,0), (-0.489968,-2.104146,0),
			(-0.476398,-2.154791,0), (-0.457608,-2.20374,0), (-0.433805,-2.250457,0),
			(-0.405248,-2.29443,0), (-0.372252,-2.335177,0), (-0.335177,-2.372252,0),
			(-0.29443,-2.405248,0), (-0.250457,-2.433805,0), (-0.20374,-2.457608,0),
			(-0.154791,-2.476398,0), (-0.104146,-2.489968,0), (-0.0523598,-2.498171,0),
			(0,-2.500915,0), (0.0523598,-2.498171,0), (0.104146,-2.489968,0),
			(0.154791,-2.476398,0), (0.20374,-2.457608,0), (0.250457,-2.433805,0),
			(0.29443,-2.405248,0), (0.335177,-2.372252,0), (0.372252,-2.335177,0),
			(0.405248,-2.29443,0), (0.433805,-2.250457,0), (0.457608,-2.20374,0),
			(0.476398,-2.154791,0), (0.489968,-2.104146,0), (0.498171,-2.05236,0),
			(0.500915,-2,0), (0.498171,-1.94764,0), (0.489968,-1.895854,0),
			(0.476398,-1.845209,0), (0.457608,-1.79626,0), (0.433805,-1.749543,0),
			(0.405248,-1.70557,0), (0.372252,-1.664823,0), (0.335177,-1.627748,0),
			(0.29443,-1.594752,0), (0.250457,-1.566195,0), (0.20374,-1.542392,0),
			(0.154791,-1.523602,0), (0.104146,-1.510032,0), (0.0523598,-1.501829,0),
			(0,-1.499085,0), (0,0,0), (0,1.499085,0), (0.0523598,1.501829,0),
			(0.104146,1.510032,0), (0.154791,1.523602,0), (0.20374,1.542392,0),
			(0.250457,1.566195,0), (0.29443,1.594752,0), (0.335177,1.627748,0),
			(0.372252,1.664823,0), (0.405248,1.70557,0), (0.433805,1.749543,0),
			(0.457608,1.79626,0), (0.476398,1.845209,0), (0.489968,1.895854,0),
			(0.498171,1.94764,0), (0.500915,2,0), (0.498171,2.05236,0),
			(0.489968,2.104146,0), (0.476398,2.154791,0), (0.457608,2.20374,0),
			(0.433805,2.250457,0), (0.405248,2.29443,0), (0.372252,2.335177,0),
			(0.335177,2.372252,0), (0.29443,2.405248,0), (0.250457,2.433805,0),
			(0.20374,2.457608,0), (0.154791,2.476398,0), (0.104146,2.489968,0),
			(0.0523598,2.498171,0), (0,2.500915,0), (-0.0523598,2.498171,0),
			(-0.104146,2.489968,0), (-0.154791,2.476398,0), (-0.20374,2.457608,0),
			(-0.250457,2.433805,0), (-0.29443,2.405248,0), (-0.335177,2.372252,0),
			(-0.372252,2.335177,0), (-0.405248,2.29443,0), (-0.433805,2.250457,0),
			(-0.457608,2.20374,0), (-0.476398,2.154791,0), (-0.489968,2.104146,0),
			(-0.498171,2.05236,0), (-0.500915,2,0), (-0.498171,1.94764,0),
			(-0.489968,1.895854,0), (-0.476398,1.845209,0), (-0.457608,1.79626,0),
			(-0.433805,1.749543,0), (-0.405248,1.70557,0), (-0.372252,1.664823,0),
			(-0.335177,1.627748,0), (-0.29443,1.594752,0), (-0.250457,1.566195,0),
			(-0.20374,1.542392,0), (-0.154791,1.523602,0), (-0.104146,1.510032,0),
			(-0.0523598,1.501829,0), (0,1.499085,0)]

		elif curveType == 'pentagon':
			parameter = [(0, 0, 1.12558), (0, 0, 1), (-1, 0, 1), (-1, 0, -0.5),
			(0, 0, -1), (0, 0, -1.12558), (0, 0, -1), (1, 0, -0.5), (1, 0, 1), (0, 0, 1)]

		elif curveType == 'null':
			parameter = [(0,0,0), (0,0,0)]
		
		else: # null shape
			parameter = [(0,0,0), (0,0,0)]
		
		return parameter

	def resetShape(self):

		shpDict = {
					80: 'sphere',
					62: 'stick',
					48: 'circle',
					29: 'crossArrow',
					27: 'capsule',
					16: 'cube',
					10: 'pentagon',
					8: 'plus',
					5: 'square'
				}

		cvsNo = mc.getAttr('%s.spans' % self.shape) + mc.getAttr('%s.degree' % self.shape)
		crvType = shpDict[cvsNo]
		parameter = self.curveParameter(crvType)

		for ix in range(cvsNo):
			currPos = parameter[ix]
			currVtx = '%s.cv[%s]' % (self.shape, str(ix))
			mc.xform(currVtx, os=True, t=(currPos[0], currPos[1], currPos[2]))

	def createCurve(self, curveType = ''):
		# Creates a curve shape for current transform object
		# Returns shape node

		curve = ''

		if curveType == 'nrbCircle':
			curve = mc.circle(d=3, s=8, ch=False)[0]
		else:
			curve = mc.curve(d = 1, p = self.curveParameter(curveType))
		
		curveShape = mc.listRelatives(curve, s = True)[0]
		
		mc.parent(curveShape, self.name, s = True, r = True)
		mc.delete(curve)
		mc.select(cl = True)
		
		return mc.rename(curveShape, '%sShape' % self.name)
	
	# Shape tools
	def scaleShape(self, val = 1.0000):
		# Scale curve shape
		if self.shape:
			typ = mc.nodeType(self.shape)
			if typ == 'nurbsCurve':
				cvsNo = mc.getAttr('%s.spans' % self.shape) + mc.getAttr('%s.degree' % self.shape)
				cvs = '%s.cv[%s:%s]' % (self.name, str(0), str(cvsNo))
				piv = mc.xform(self.name, q = True, t = True, ws = True)
			elif typ == 'nurbsSurface':
				cvU = mc.getAttr('%s.spansU' % self.shape) + mc.getAttr('%s.degreeU' % self.shape) - 1
				cvV = mc.getAttr('%s.spansV' % self.shape) + mc.getAttr('%s.degreeV' % self.shape) - 1
				cvs = '%s.cv[%s:%s][%s:%s]' % (self.name, str(0), str(cvU), str(0), str(cvV))
				piv = mc.xform(self.name, q = True, t = True, ws = True)
			
			mc.scale(val, val, val, cvs, pivot = (piv[0], piv[1], piv[2]), r = True)
	
	def rotateShape(self, ro = (0, 0, 0) ):
		# Rotate curve shape
		if self.shape:
			typ = mc.nodeType(self.shape)
			if typ == 'nurbsCurve':
				cvsNo = mc.getAttr('%s.spans' % self.shape) + mc.getAttr('%s.degree' % self.shape)
				cvs = '%s.cv[%s:%s]' % (self.name, str(0), str(cvsNo))
			elif typ == 'nurbsSurface':
				cvU = mc.getAttr('%s.spansU' % self.shape) + mc.getAttr('%s.degreeU' % self.shape) - 1
				cvV = mc.getAttr('%s.spansV' % self.shape) + mc.getAttr('%s.degreeV' % self.shape) - 1
				cvs = '%s.cv[%s:%s][%s:%s]' % (self.name, str(0), str(cvU), str(0), str(cvV))
			
			mc.rotate(ro[0], ro[1], ro[2], cvs, r = True, os = True)

	def moveShape(self, mo = (0, 0, 0) ):
		# Move curve shape
		if self.shape:
			typ = mc.nodeType(self.shape)
			if typ == 'nurbsCurve':
				cvsNo = mc.getAttr('%s.spans' % self.shape) + mc.getAttr('%s.degree' % self.shape)
				cvs = '%s.cv[%s:%s]' % (self.name, str(0), str(cvsNo))
			elif typ == 'nurbsSurface':
				cvU = mc.getAttr('%s.spansU' % self.shape) + mc.getAttr('%s.degreeU' % self.shape) - 1
				cvV = mc.getAttr('%s.spansV' % self.shape) + mc.getAttr('%s.degreeV' % self.shape) - 1
				cvs = '%s.cv[%s:%s][%s:%s]' % (self.name, str(0), str(cvU), str(0), str(cvV))
			
			mc.move(mo[0], mo[1], mo[2], cvs, r = True, os = True)

	
	# Hide/Show object
	def hide(self):
		
		if self.attr('v').l:
			self.attr('v').l = 0
			self.attr('v').v = 0
			self.attr('v').l = 1
		else:
			self.attr('v').v = 0
	
	def show(self):
		
		if self.attr('v').l:
			self.attr('v').l = 0
			self.attr('v').v = 1
			self.attr('v').l = 1
		else:
			self.attr('v').v = 1

class Locator(Dag):
	# Locator object
	def __init__(self):
		Dag.__init__(self, mc.spaceLocator()[0])

class Joint(Dag):
	# Joint object
	def __init__(self, curveType = ''):
		Dag.__init__(self, mc.createNode('joint'))
		if curveType: self.createCurve(curveType)

class Control(Dag):
	# Control object
	# If no curveType specified, create an empty group
	def __init__(self, curveType = ''):
		Dag.__init__(self, mc.group(em = True))
		if curveType: self.createCurve(curveType)

class JoyStick(Control):
	# Joy stick control for facial control
	def __init__(self):
		
		self.bshCtrl_grp = Null()
		self.bsh_ctrl = Control(curveType = 'circle')
		self.bshBrdr_crv = Control(curveType = 'grid')
		
		# Parenting
		self.bsh_ctrl.parent(self.bshBrdr_crv)
		self.bshBrdr_crv.parent(self.bshCtrl_grp)
		
		# Adjusting controller shape
		self.bsh_ctrl.rotateShape((90, 0, 0))
		self.bsh_ctrl.scaleShape(0.2)
		
		# Adjusting board shape
		brdShp = Dag(self.bshBrdr_crv.shape)
		brdShp.attr('overrideEnabled').v = 1
		brdShp.attr('overrideDisplayType').v = 1
		
		# Cleanup
		attrs = ('tz', 'sx', 'sy', 'sz', 'v')
		for attr in attrs:
			self.bsh_ctrl.attr(attr).lockHide()
		
		# Limit translations
		self.bsh_ctrl.attr('xtxe').value = 1
		self.bsh_ctrl.attr('mtxe').value = 1
		self.bsh_ctrl.attr('xtye').value = 1
		self.bsh_ctrl.attr('mtye').value = 1
		
		self.bsh_ctrl.attr('xtxl').value = 1
		self.bsh_ctrl.attr('mtxl').value = -1
		self.bsh_ctrl.attr('xtyl').value = 1
		self.bsh_ctrl.attr('mtyl').value = -1

class Null(Dag):
	def __init__(self, nodeName=''):
		Dag.__init__(self, mc.group(em = True, n=nodeName))

class Ik(Dag):
	# Template class for IK handle object in this module
	def __init__(self, nodeName = ''):
		Dag.__init__(self, nodeName)
		
		# name overriding
		self.__name = nodeName
	
	# Name properties
	def getName(self):
		return self.__name
	
	def rename(self, newName):
		self.__name = mc.rename(self.__name, newName)
		self.eff = '%sEff' % newName
	
	name = property(getName, rename, None, None)
	
	# Eff property
	def getEff(self):
		return mc.listConnections('%s.endEffector' % self.__name, s = True, d = False)[0]
	
	def setEff(self, newName = ''):
		mc.rename(self.eff, newName)
	
	eff = property(getEff, setEff, None, None)

class IkRp(Ik):
	# IKRP object
	def __init__(self, sj = '', ee = ''):
		Ik.__init__(self, mc.ikHandle(sj = sj, ee = ee, sol = 'ikRPsolver')[0])

class IkSc(Ik):
	# IKSC object
	def __init__(self, sj = '', ee = ''):
		Ik.__init__(self, mc.ikHandle(sj = sj, ee = ee, sol = 'ikSCsolver')[0])

class IkShoot(Ik):
	# IK object
	def __init__(self, **kwargs):
		
		cmd = 'mc.ikHandle('
		cmd += addArgs(**kwargs)
		cmd += ')'
		
		Ik.__init__(self, eval(cmd)[0])
		
class Constraint(Dag):
	# Template class for constraint object in this module
	def __init__(self, nodeName = ''):
		Dag.__init__(self, nodeName)
	
	# target property
	def getTargets(self):
		return mc.listConnections('%s.target' % self.name, s = True)
	
	target = property(getTargets, None, None, None)

class ParentConstraint(Constraint):
	# parentConstraint object
	def __init__(self):
		
		Constraint.__init__(self, mc.createNode('parentConstraint'))

class ScaleConstraint(Constraint):
	# scaleConstraint object
	def __init__(self):
		
		Constraint.__init__(self, mc.createNode('scaleConstraint'))

class PointConstraint(Constraint):
	# pointConstraint object
	def __init__(self ):
		
		Constraint.__init__(self, mc.createNode('pointConstraint'))

class OrientConstraint(Constraint):
	# orientConstraint object
	def __init__(self ):
		
		Constraint.__init__(self, mc.createNode('orientConstraint'))

class PoleVectorConstraint(Constraint):
	# poleVectorConstraint object
	def __init__(self ):
		
		Constraint.__init__(self, mc.createNode('poleVectorConstraint'))

class TangentConstraint(Constraint):
	# tangentConstraint object
	def __init__(self ):
		
		Constraint.__init__(self, mc.createNode('tangentConstraint'))

class AimConstraint(Constraint):
	# aimConstraint object
	def __init__(self ):
		
		Constraint.__init__(self, mc.createNode('aimConstraint'))
