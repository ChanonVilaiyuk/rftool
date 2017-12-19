import os 
import sys 
import logging 

import maya.cmds as mc 
import maya.mel as mm 

from functools import partial 

class Window: 
	name = 'ClipboardWin'
	ui = 'clipboard'
	w = 200
	h = 104

class Name: 
	dirname = os.environ.get('TEMP')
	filename = 'mayaClipboardTmp.ma' 
	cliboard = '%s/%s' % (dirname, filename)

def deleteUI(ui): 
	if mc.window(ui, exists=True): 
		mc.deleteUI(ui)
		deleteUI(ui)

def show(): 
	deleteUI(Window.name)
	app = ClipboardUI()
	app.show()
	return app

class ClipboardUI(object):
	"""docstring for ClipboardUI"""
	def __init__(self):
		super(ClipboardUI, self).__init__()


	def show(self): 
		win = mc.window(Window.name, t='Clipboard')
		mc.columnLayout(adj=1, rs=4)
		mc.text(l='Local Cliboard', al='center')
		mc.button(l='Copy', h=30, bgc=(0.5, 1, 0.5), c=partial(self.copy))
		mc.button(l='Paste', h=30, bgc=(1, 0.5, 0.5), c=partial(self.paste))
		mc.text('%s_label' % Window.ui, l='')
		mc.showWindow()
		mc.window(Window.name, e=True, wh=[Window.w, Window.h])


	def copy(self, *args): 
		if mc.ls(sl=True): 
			result = mc.file(Name.cliboard, force=True, options='v=0', typ='mayaAscii', pr=True, es=True) 
			mc.text('%s_label' % Window.ui, e=True, l='Copied', bgc=(0.2, 1, 0.2))
			return result
		else: 
			mc.text('%s_label' % Window.ui, e=True, l='Select object to copy', bgc=(1, 0.2, 0.2))

	def paste(self, *args): 
		if os.path.exists(Name.cliboard): 
			mc.file(Name.cliboard,  i=True, type='mayaAscii', options='v=0', pr=True, loadReferenceDepth='all') 

		else: 
			mc.text('%s_label' % Window.ui, e=True, l='No Clipboard', bgc=(1, 0.2, 0.2))


		